"""Celery app + weekly beat schedule for re-scraping every source.

Run locally:
    celery -A app.scrapers.scheduler worker --loglevel=info
    celery -A app.scrapers.scheduler beat   --loglevel=info
Trigger manually:  python -m app.cli scrape --source all
"""

from __future__ import annotations

import asyncio
import logging

from celery import Celery
from celery.schedules import crontab

from app.config import settings

logger = logging.getLogger(__name__)

broker = settings.redis_url or "memory://"
celery_app = Celery("africadata", broker=broker, backend=settings.redis_url or None)
celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    beat_schedule={
        # World Bank refreshes WDI on a rolling basis; Sunday 02:00 UTC keeps us within a week.
        "scrape-world-bank-weekly": {"task": "scrapers.world_bank", "schedule": crontab(hour=2, minute=0, day_of_week="sunday")},
        "scrape-imf-weekly": {"task": "scrapers.imf", "schedule": crontab(hour=3, minute=0, day_of_week="sunday")},
        "scrape-who-weekly": {"task": "scrapers.who", "schedule": crontab(hour=3, minute=30, day_of_week="sunday")},
        "scrape-un-weekly": {"task": "scrapers.un_data", "schedule": crontab(hour=4, minute=0, day_of_week="sunday")},
    },
)


def _run(coro) -> dict:
    stats = asyncio.run(coro)
    from app.middleware.response_cache import invalidate_response_cache

    invalidate_response_cache()
    return stats.as_dict()


@celery_app.task(name="scrapers.world_bank")
def scrape_world_bank(only_codes: list[str] | None = None) -> dict:
    from app.scrapers.world_bank import scrape_all

    return _run(scrape_all(only_codes=only_codes))


@celery_app.task(name="scrapers.imf")
def scrape_imf() -> dict:
    from app.scrapers.imf import scrape_all

    return _run(scrape_all())


@celery_app.task(name="scrapers.who")
def scrape_who() -> dict:
    from app.scrapers.who import scrape_all

    return _run(scrape_all())


@celery_app.task(name="scrapers.un_data")
def scrape_un_data() -> dict:
    from app.scrapers.un_data import scrape_all

    return _run(scrape_all())


@celery_app.task(name="scrapers.afdb")
def scrape_afdb() -> dict:
    from app.scrapers.afdb import scrape_all

    return _run(scrape_all())


@celery_app.task(name="scrapers.all")
def scrape_everything() -> dict:
    return {
        "world_bank": scrape_world_bank(),
        "imf": scrape_imf(),
        "who": scrape_who(),
        "un_data": scrape_un_data(),
        "afdb": scrape_afdb(),
    }
