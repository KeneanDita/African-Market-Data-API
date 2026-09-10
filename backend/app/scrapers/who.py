"""WHO Global Health Observatory scraper (OData API, no key required).

Primary source for OBESITY_ADULT; WDI does not carry a maintained obesity series.
API: https://ghoapi.azureedge.net/api/{INDICATOR}?$filter=SpatialDim eq 'ETH' ...
"""

from __future__ import annotations

import asyncio
import logging

import httpx

from app.scrapers.base import BaseScraper, Observation
from app.utils.countries_seed import AFRICAN_ISO3_CODES, ISO3_TO_ISO2

logger = logging.getLogger(__name__)

WHO_BASE = "https://ghoapi.azureedge.net/api"

# GHO indicators have a sex dimension; we take "both sexes".
BOTH_SEXES = "SEX_BTSX"


class WHOScraper(BaseScraper):
    source = "WHO"

    async def fetch(self, client: httpx.AsyncClient, gho_code: str) -> list[dict]:
        rows: list[dict] = []
        # Filter server-side to African countries in chunks to keep URLs short.
        for i in range(0, len(AFRICAN_ISO3_CODES), 18):
            chunk = AFRICAN_ISO3_CODES[i : i + 18]
            spatial = " or ".join(f"SpatialDim eq '{c}'" for c in chunk)
            params = {"$filter": f"({spatial}) and Dim1 eq '{BOTH_SEXES}'"}
            resp = await client.get(f"{WHO_BASE}/{gho_code}", params=params)
            resp.raise_for_status()
            rows.extend(resp.json().get("value", []))
            await asyncio.sleep(0.3)
        return rows

    async def scrape(self, client: httpx.AsyncClient) -> None:
        indicators = self.indicators_for_source()
        country_map = self.countries_by_iso2()
        for code, indicator in indicators.items():
            try:
                rows = await self.fetch(client, indicator.source_code)
            except Exception as exc:  # noqa: BLE001
                self.stats.errors += 1
                logger.error("[WHO] %s (%s) failed: %s", code, indicator.source_code, exc)
                continue
            observations: list[Observation] = []
            for row in rows:
                iso2 = ISO3_TO_ISO2.get(row.get("SpatialDim", ""))
                if not iso2:
                    continue
                obs = self.to_observation(iso2, code, row.get("TimeDim"), row.get("NumericValue"))
                if obs and self.from_year <= obs.year <= self.to_year:
                    observations.append(obs)
            self.stats.fetched += len(observations)
            self.upsert(indicator, observations, country_map)
            logger.info("[WHO] %-32s %5d points", code, len(observations))


async def scrape_all(from_year: int | None = None, to_year: int | None = None):
    from app.config import settings

    return await WHOScraper(from_year=from_year or settings.scrape_from_year, to_year=to_year or settings.scrape_to_year).run()


if __name__ == "__main__":
    asyncio.run(scrape_all())
