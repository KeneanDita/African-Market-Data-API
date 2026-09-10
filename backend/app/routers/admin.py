"""Operator endpoints, protected by `ADMIN_TOKEN` (X-Admin-Token header).

Exists so a deployment without shell access or a paid worker (Render/Railway free tiers) can
still be seeded and refreshed: a GitHub Actions cron calls POST /v1/admin/scrape weekly and
polls GET /v1/admin/scrape/status until it finishes.
"""

from __future__ import annotations

import asyncio
import logging
import secrets
import threading
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Header, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.config import settings
from app.database import SessionLocal, get_db
from app.models import Country, DataPoint, Indicator

logger = logging.getLogger(__name__)
router = APIRouter()

SOURCES = ("world_bank", "imf", "who", "un_data", "afdb")

_state: dict = {"running": False, "started_at": None, "finished_at": None, "sources": [], "results": {}, "error": None}
_lock = threading.Lock()


def require_admin(x_admin_token: str | None = Header(default=None)) -> None:
    if not settings.admin_token:
        raise HTTPException(status_code=404, detail="Admin routes are disabled (ADMIN_TOKEN not set)")
    if not x_admin_token or not secrets.compare_digest(x_admin_token, settings.admin_token):
        raise HTTPException(status_code=401, detail="Invalid admin token")


class ScrapeRequest(BaseModel):
    sources: list[str] = Field(default_factory=lambda: list(SOURCES))
    from_year: int | None = None
    to_year: int | None = None
    only: list[str] | None = Field(default=None, description="Indicator codes (world_bank only)")


async def _run_sources(req: ScrapeRequest) -> dict:
    results = {}
    for src in req.sources:
        if src == "world_bank":
            from app.scrapers.world_bank import scrape_all

            stats = await scrape_all(req.from_year, req.to_year, only_codes=req.only)
        else:
            module = __import__(f"app.scrapers.{src}", fromlist=["scrape_all"])
            stats = await module.scrape_all(req.from_year, req.to_year)
        results[src] = stats.as_dict()
    return results


def _worker(req: ScrapeRequest) -> None:
    try:
        results = asyncio.run(_run_sources(req))
        from app.middleware.response_cache import invalidate_response_cache

        invalidate_response_cache()
        with _lock:
            _state.update(results=results, error=None)
    except Exception as exc:  # noqa: BLE001
        logger.exception("admin scrape failed")
        with _lock:
            _state.update(error=str(exc))
    finally:
        with _lock:
            _state.update(running=False, finished_at=datetime.now(timezone.utc).isoformat())


@router.post("/seed", dependencies=[Depends(require_admin)], summary="Seed countries and indicators")
def seed():
    from app.utils.countries_seed import seed_countries
    from app.utils.indicators_seed import seed_indicators

    with SessionLocal() as db:
        return {"countries_created": seed_countries(db), "indicators_created": seed_indicators(db)}


@router.post("/scrape", dependencies=[Depends(require_admin)], status_code=202, summary="Start a background scrape")
def start_scrape(req: ScrapeRequest):
    unknown = [s for s in req.sources if s not in SOURCES]
    if unknown:
        raise HTTPException(status_code=400, detail=f"Unknown source(s): {', '.join(unknown)}. Valid: {', '.join(SOURCES)}")
    with _lock:
        if _state["running"]:
            raise HTTPException(status_code=409, detail="A scrape is already running")
        _state.update(running=True, started_at=datetime.now(timezone.utc).isoformat(), finished_at=None, sources=req.sources, results={}, error=None)
    threading.Thread(target=_worker, args=(req,), daemon=True, name="admin-scrape").start()
    return {"status": "started", "sources": req.sources, "poll": "/v1/admin/scrape/status"}


@router.get("/scrape/status", dependencies=[Depends(require_admin)], summary="Progress of the last scrape")
def scrape_status(db: Session = Depends(get_db)):
    with _lock:
        snapshot = dict(_state)
    snapshot["database"] = {
        "countries": db.query(func.count(Country.id)).scalar(),
        "indicators": db.query(func.count(Indicator.id)).scalar(),
        "data_points": db.query(func.count(DataPoint.id)).scalar(),
        "indicators_with_data": db.query(func.count(func.distinct(DataPoint.indicator_id))).scalar(),
    }
    return snapshot
