"""World Bank World Development Indicators scraper.

Covers ~80 of the 87 indicators. We request `country/all` for each indicator (one paginated call,
~3.5 MB, all economies and years) and keep only African rows client-side. Listing the 54 ISO codes
in the path trips the World Bank WAF (403) once the URL gets long, so `all` is both simpler and safer.
Docs: https://datahelpdesk.worldbank.org/knowledgebase/articles/898581
"""

from __future__ import annotations

import asyncio
import logging

import httpx
from sqlalchemy import func

from app.models.country import Country
from app.models.data_point import DataPoint
from app.models.indicator import Indicator
from app.scrapers.base import BaseScraper, Observation
from app.utils.countries_seed import AFRICAN_ISO2_CODES

logger = logging.getLogger(__name__)

WORLD_BANK_BASE = "https://api.worldbank.org/v2"
PER_PAGE = 20000
CONCURRENCY = 3
POLITE_DELAY_SECONDS = 0.5


class WorldBankScraper(BaseScraper):
    source = "World Bank"

    def __init__(self, *args, only_codes: list[str] | None = None, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.only_codes = set(only_codes) if only_codes else None

    async def fetch_indicator(self, client: httpx.AsyncClient, wb_code: str) -> list[dict]:
        url = f"{WORLD_BANK_BASE}/country/all/indicator/{wb_code}"
        params = {"format": "json", "per_page": PER_PAGE, "date": f"{self.from_year}:{self.to_year}", "page": 1}
        items: list[dict] = []
        while True:
            resp = await client.get(url, params=params)
            resp.raise_for_status()
            payload = resp.json()
            if not isinstance(payload, list) or len(payload) < 2:
                # WDI returns [{"message": [...]}] for unknown indicators
                logger.warning("[World Bank] %s: unexpected payload %s", wb_code, str(payload)[:200])
                return items
            meta, rows = payload[0], payload[1] or []
            items.extend(rows)
            if params["page"] >= int(meta.get("pages", 1)):
                break
            params["page"] += 1
        return items

    async def scrape(self, client: httpx.AsyncClient) -> None:
        indicators = self.indicators_for_source()
        if self.only_codes:
            indicators = {k: v for k, v in indicators.items() if k in self.only_codes}
        country_map = self.countries_by_iso2()
        wanted = {c for c in AFRICAN_ISO2_CODES if c in country_map}
        sem = asyncio.Semaphore(CONCURRENCY)

        async def worker(indicator: Indicator) -> tuple[Indicator, list[Observation]]:
            async with sem:
                try:
                    rows = await self.fetch_indicator(client, indicator.source_code)
                except Exception as exc:  # noqa: BLE001
                    self.stats.errors += 1
                    logger.error("[World Bank] %s (%s) failed: %s", indicator.code, indicator.source_code, exc)
                    return indicator, []
                await asyncio.sleep(POLITE_DELAY_SECONDS)
            observations = []
            for row in rows:
                iso2 = (row.get("country") or {}).get("id")
                if iso2 not in wanted:
                    continue
                obs = self.to_observation(iso2, indicator.code, row.get("date"), row.get("value"))
                if obs:
                    observations.append(obs)
            self.stats.fetched += len(observations)
            return indicator, observations

        for coro in asyncio.as_completed([worker(ind) for ind in indicators.values()]):
            indicator, observations = await coro
            self.upsert(indicator, observations, country_map)
            logger.info("[World Bank] %-32s %5d points", indicator.code, len(observations))

    def after_run(self) -> None:
        """Copy the latest POPULATION_TOTAL into countries.population for quick country listings."""
        pop = self.db.query(Indicator).filter(Indicator.code == "POPULATION_TOTAL").first()
        if not pop:
            return
        latest_year = (
            self.db.query(DataPoint.country_id, func.max(DataPoint.year).label("year"))
            .filter(DataPoint.indicator_id == pop.id, DataPoint.value.isnot(None))
            .group_by(DataPoint.country_id)
            .subquery()
        )
        rows = (
            self.db.query(DataPoint.country_id, DataPoint.value)
            .join(latest_year, (latest_year.c.country_id == DataPoint.country_id) & (latest_year.c.year == DataPoint.year))
            .filter(DataPoint.indicator_id == pop.id)
            .all()
        )
        values = {cid: int(v) for cid, v in rows if v is not None}
        for country in self.db.query(Country).all():
            if country.id in values:
                country.population = values[country.id]
        self.db.commit()


async def scrape_all(from_year: int | None = None, to_year: int | None = None, only_codes: list[str] | None = None):
    from app.config import settings

    scraper = WorldBankScraper(from_year=from_year or settings.scrape_from_year, to_year=to_year or settings.scrape_to_year, only_codes=only_codes)
    return await scraper.run()


if __name__ == "__main__":
    asyncio.run(scrape_all())
