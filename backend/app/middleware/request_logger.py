"""Writes one `request_logs` row per API call and refreshes `api_users.last_seen_at`."""

from __future__ import annotations

import logging
import time
from datetime import datetime, timezone

from fastapi import Request
from sqlalchemy import update
from starlette.middleware.base import BaseHTTPMiddleware

from app.config import settings
from app.database import SessionLocal
from app.middleware.api_key_auth import is_public_path
from app.models.api_user import ApiUser
from app.models.request_log import RequestLog

logger = logging.getLogger(__name__)


class RequestLoggerMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start = time.perf_counter()
        response = await call_next(request)
        elapsed_ms = int((time.perf_counter() - start) * 1000)
        response.headers["X-Response-Time"] = f"{elapsed_ms}ms"

        if not settings.log_requests or is_public_path(request.url.path, request.method):
            return response

        auth = getattr(request.state, "auth", None)
        key_hash = auth.key_hash if auth else None
        forwarded = request.headers.get("x-forwarded-for")
        ip = forwarded.split(",")[0].strip() if forwarded else (request.client.host if request.client else None)

        db = SessionLocal()
        try:
            db.add(RequestLog(
                api_key_hash=key_hash,
                endpoint=request.url.path[:200],
                method=request.method,
                status_code=response.status_code,
                response_ms=elapsed_ms,
                ip_address=(ip or "")[:45] or None,
            ))
            if key_hash and not key_hash.startswith("anon"):
                db.execute(update(ApiUser).where(ApiUser.api_key_hash == key_hash).values(last_seen_at=datetime.now(timezone.utc)))
            db.commit()
        except Exception as exc:  # noqa: BLE001 - logging must never break a request
            db.rollback()
            logger.warning("request log write failed: %s", exc)
        finally:
            db.close()
        return response
