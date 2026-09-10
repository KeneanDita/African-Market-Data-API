"""UN Population Division (World Population Prospects) scraper.

Primary source for MEDIAN_AGE. The UN Data Portal API requires a free bearer token since 2024;
set UN_DATA_API_TOKEN in the environment (request one at https://population.un.org/dataportal/about/dataapi).
Without a token the scraper logs a notice and exits cleanly so scheduled runs never fail.
"""

from __future__ import annotations

import asyncio
import logging

import httpx

from app.config import settings
from app.scrapers.base import BaseScraper, Observation
from app.utils.countries_seed import ISO3_TO_ISO2

logger = logging.getLogger(__name__)

UN_BASE = "https://population.un.org/dataportalapi/api/v1"
# WPP indicator id for "Median age of population" and the UN M49 codes for our countries.
UN_INDICATOR_IDS = {"WPP:MedianAgePop": 67}
UN_LOCATION_M49: dict[str, int] = {
    "DZA": 12, "EGY": 818, "LBY": 434, "MAR": 504, "SDN": 729, "TUN": 788,
    "BEN": 204, "BFA": 854, "CPV": 132, "CIV": 384, "GMB": 270, "GHA": 288, "GIN": 324, "GNB": 624,
    "LBR": 430, "MLI": 466, "MRT": 478, "NER": 562, "NGA": 566, "SEN": 686, "SLE": 694, "TGO": 768,
    "BDI": 108, "COM": 174, "DJI": 262, "ERI": 232, "ETH": 231, "KEN": 404, "MDG": 450, "MWI": 454,
    "MUS": 480, "MOZ": 508, "RWA": 646, "SYC": 690, "SOM": 706, "SSD": 728, "TZA": 834, "UGA": 800,
    "ZMB": 894, "ZWE": 716,
    "AGO": 24, "CMR": 120, "CAF": 140, "TCD": 148, "COG": 178, "COD": 180, "GNQ": 226, "GAB": 266, "STP": 678,
    "BWA": 72, "SWZ": 748, "LSO": 426, "NAM": 516, "ZAF": 710,
}
M49_TO_ISO3 = {v: k for k, v in UN_LOCATION_M49.items()}


class UNDataScraper(BaseScraper):
    source = "UN Population Division"

    def http_client(self) -> httpx.AsyncClient:
        client = super().http_client()
        if settings.un_data_api_token:
            client.headers["Authorization"] = f"Bearer {settings.un_data_api_token}"
        return client

    async def fetch(self, client: httpx.AsyncClient, indicator_id: int) -> list[dict]:
        locations = ",".join(str(m) for m in UN_LOCATION_M49.values())
        url = f"{UN_BASE}/data/indicators/{indicator_id}/locations/{locations}/start/{self.from_year}/end/{self.to_year}"
        rows: list[dict] = []
        params = {"pageSize": 1000, "pageNumber": 1, "format": "json"}
        while True:
            resp = await client.get(url, params=params)
            resp.raise_for_status()
            payload = resp.json()
            rows.extend(payload.get("data", []))
            if params["pageNumber"] >= int(payload.get("pages", 1)):
                break
            params["pageNumber"] += 1
        return rows

    async def scrape(self, client: httpx.AsyncClient) -> None:
        if not settings.un_data_api_token:
            logger.warning("[UN] UN_DATA_API_TOKEN not set; skipping (MEDIAN_AGE will stay empty).")
            return
        indicators = self.indicators_for_source()
        country_map = self.countries_by_iso2()
        for code, indicator in indicators.items():
            un_id = UN_INDICATOR_IDS.get(indicator.source_code or "")
            if un_id is None:
                continue
            try:
                rows = await self.fetch(client, un_id)
            except Exception as exc:  # noqa: BLE001
                self.stats.errors += 1
                logger.error("[UN] %s failed: %s", code, exc)
                continue
            observations: list[Observation] = []
            for row in rows:
                # Only the "Median" variant, both sexes; WPP publishes estimates and projections.
                if row.get("variant") not in (None, "Median") or row.get("sex") not in (None, "Both sexes"):
                    continue
                iso3 = M49_TO_ISO3.get(int(row.get("locationId", 0)))
                iso2 = ISO3_TO_ISO2.get(iso3 or "")
                if not iso2:
                    continue
                obs = self.to_observation(iso2, code, row.get("timeLabel"), row.get("value"))
                if obs:
                    observations.append(obs)
            self.stats.fetched += len(observations)
            self.upsert(indicator, observations, country_map)
            logger.info("[UN] %-32s %5d points", code, len(observations))


async def scrape_all(from_year: int | None = None, to_year: int | None = None):
    return await UNDataScraper(from_year=from_year or settings.scrape_from_year, to_year=to_year or settings.scrape_to_year).run()


if __name__ == "__main__":
    asyncio.run(scrape_all())
