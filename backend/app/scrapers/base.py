"""Shared plumbing for data-source scrapers.

Every scraper produces `Observation`s; `BaseScraper.upsert()` writes them with a single
"load existing -> diff -> bulk insert/update" pass per indicator so a full refresh of one
indicator across 54 countries and 60+ years is a handful of statements, not thousands.
"""

from __future__ import annotations

import abc
import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal

import httpx
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.country import Country
from app.models.data_point import DataPoint
from app.models.indicator import Indicator
from app.utils.normalizer import parse_number, parse_year

logger = logging.getLogger(__name__)

# Higher wins when two sources report the same (country, indicator, year).
SOURCE_PRIORITY: dict[str, int] = {"World Bank": 3, "WHO": 3, "UN Population Division": 3, "IMF": 2, "African Development Bank": 1}


@dataclass(frozen=True)
class Observation:
    iso2: str
    indicator_code: str
    year: int
    value: Decimal


@dataclass
class ScrapeStats:
    source: str
    fetched: int = 0
    inserted: int = 0
    updated: int = 0
    skipped: int = 0
    errors: int = 0

    def as_dict(self) -> dict:
        return self.__dict__.copy()


class BaseScraper(abc.ABC):
    source: str = "unknown"
    fill_gaps_only: bool = False  # secondary sources never overwrite a higher-priority value
    request_timeout: float = 60.0
    user_agent = "AfricanMarketDataAPI/1.0 (+https://africadata.dev)"

    def __init__(self, db: Session | None = None, from_year: int = 1960, to_year: int = 2025) -> None:
        self._db = db
        self._owns_db = db is None
        self.from_year = from_year
        self.to_year = to_year
        self.stats = ScrapeStats(source=self.source)

    # ---------------------------------------------------------------- lifecycle

    @property
    def db(self) -> Session:
        if self._db is None:
            self._db = SessionLocal()
        return self._db

    def close(self) -> None:
        if self._owns_db and self._db is not None:
            self._db.close()
            self._db = None

    def http_client(self) -> httpx.AsyncClient:
        return httpx.AsyncClient(
            timeout=self.request_timeout,
            headers={"User-Agent": self.user_agent, "Accept": "application/json"},
            follow_redirects=True,
        )

    async def run(self) -> ScrapeStats:
        logger.info("[%s] starting scrape %s-%s", self.source, self.from_year, self.to_year)
        try:
            async with self.http_client() as client:
                await self.scrape(client)
            self.after_run()
        finally:
            self.close()
        logger.info("[%s] done: %s", self.source, self.stats.as_dict())
        return self.stats

    @abc.abstractmethod
    async def scrape(self, client: httpx.AsyncClient) -> None:
        """Fetch upstream data and call `self.upsert(...)` per indicator."""

    def after_run(self) -> None:  # noqa: B027 - optional hook
        pass

    # ---------------------------------------------------------------- lookups

    def countries_by_iso2(self) -> dict[str, Country]:
        return {c.iso2: c for c in self.db.query(Country).all()}

    def countries_by_iso3(self) -> dict[str, Country]:
        return {c.iso3: c for c in self.db.query(Country).all()}

    def indicators_for_source(self) -> dict[str, Indicator]:
        """Indicators this source is responsible for, keyed by our internal code."""
        rows = self.db.query(Indicator).filter(Indicator.source == self.source, Indicator.source_code.isnot(None)).all()
        return {i.code: i for i in rows}

    # ---------------------------------------------------------------- writes

    def upsert(self, indicator: Indicator, observations: list[Observation], country_map: dict[str, Country]) -> None:
        if not observations:
            return
        existing: dict[tuple[int, int], DataPoint] = {
            (dp.country_id, dp.year): dp
            for dp in self.db.query(DataPoint).filter(DataPoint.indicator_id == indicator.id).all()
        }
        my_priority = SOURCE_PRIORITY.get(self.source, 0)
        now = datetime.now(timezone.utc)
        new_rows: list[DataPoint] = []

        for obs in observations:
            country = country_map.get(obs.iso2)
            if country is None:
                self.stats.skipped += 1
                continue
            current = existing.get((country.id, obs.year))
            if current is None:
                new_rows.append(DataPoint(country_id=country.id, indicator_id=indicator.id, year=obs.year, value=obs.value, source=self.source, scraped_at=now))
                continue
            theirs = SOURCE_PRIORITY.get(current.source or "", 0)
            if current.source != self.source and (self.fill_gaps_only or theirs > my_priority) and current.value is not None:
                self.stats.skipped += 1
                continue
            if current.value != obs.value or current.source != self.source:
                current.value = obs.value
                current.source = self.source
                current.scraped_at = now
                self.stats.updated += 1

        if new_rows:
            self.db.bulk_save_objects(new_rows)
            self.stats.inserted += len(new_rows)
        self.db.commit()

    # ---------------------------------------------------------------- helpers

    @staticmethod
    def to_observation(iso2: str, code: str, year_raw, value_raw) -> Observation | None:
        year = parse_year(year_raw)
        value = parse_number(value_raw)
        if year is None or value is None:
            return None
        return Observation(iso2=iso2, indicator_code=code, year=year, value=value)
