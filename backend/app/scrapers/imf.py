"""IMF World Economic Outlook scraper (DataMapper API, no key required).

Primary source for GOVERNMENT_DEBT_GDP and FISCAL_BALANCE_GDP; also fills gaps for a few
indicators where WDI coverage of African economies is thin (recent GDP growth, inflation,
current account). Values for future years are WEO projections and are excluded.
API shape: GET https://www.imf.org/external/datamapper/api/v1/{CODE}
        -> {"values": {"CODE": {"ETH": {"2000": 8.1, ...}, ...all economies}}}
The endpoint ignores country filters (and 404s on long paths), so we fetch everything and keep Africa.
"""

from __future__ import annotations

import asyncio
import logging
from datetime import date

import httpx

from app.models.indicator import Indicator
from app.scrapers.base import BaseScraper, Observation
from app.utils.countries_seed import ISO3_TO_ISO2

logger = logging.getLogger(__name__)

IMF_BASE = "https://www.imf.org/external/datamapper/api/v1"

# our code -> WEO code. Indicators whose Indicator.source == "IMF" are primary; the rest are gap fillers.
IMF_INDICATOR_MAP: dict[str, str] = {
    "GOVERNMENT_DEBT_GDP": "GGXWDG_NGDP",
    "FISCAL_BALANCE_GDP": "GGXCNL_NGDP",
    "GDP_GROWTH_ANNUAL": "NGDP_RPCH",
    "INFLATION_ANNUAL": "PCPIPCH",
    "CURRENT_ACCOUNT_BALANCE_GDP": "BCA_NGDPD",
    "GDP_PER_CAPITA_USD": "NGDPDPC",
    "UNEMPLOYMENT_RATE": "LUR",
}


class IMFScraper(BaseScraper):
    source = "IMF"
    fill_gaps_only = True

    async def fetch(self, client: httpx.AsyncClient, weo_code: str) -> dict[str, dict[str, float]]:
        resp = await client.get(f"{IMF_BASE}/{weo_code}")
        resp.raise_for_status()
        return (resp.json().get("values") or {}).get(weo_code, {})

    async def scrape(self, client: httpx.AsyncClient) -> None:
        indicators = {i.code: i for i in self.db.query(Indicator).filter(Indicator.code.in_(IMF_INDICATOR_MAP)).all()}
        country_map = self.countries_by_iso2()
        last_actual_year = date.today().year - 1  # WEO current-year figures are estimates

        for our_code, weo_code in IMF_INDICATOR_MAP.items():
            indicator = indicators.get(our_code)
            if not indicator:
                continue
            try:
                by_iso3 = await self.fetch(client, weo_code)
            except Exception as exc:  # noqa: BLE001
                self.stats.errors += 1
                logger.error("[IMF] %s (%s) failed: %s", our_code, weo_code, exc)
                continue

            observations: list[Observation] = []
            for iso3, series in by_iso3.items():
                iso2 = ISO3_TO_ISO2.get(iso3)
                if not iso2:
                    continue
                for year_raw, value in (series or {}).items():
                    obs = self.to_observation(iso2, our_code, year_raw, value)
                    if obs and self.from_year <= obs.year <= min(self.to_year, last_actual_year):
                        observations.append(obs)
            self.stats.fetched += len(observations)
            # Primary IMF indicators overwrite; the rest only fill gaps left by the World Bank.
            self.fill_gaps_only = indicator.source != self.source
            self.upsert(indicator, observations, country_map)
            logger.info("[IMF] %-32s %5d points", our_code, len(observations))
            await asyncio.sleep(0.5)


async def scrape_all(from_year: int | None = None, to_year: int | None = None):
    from app.config import settings

    return await IMFScraper(from_year=from_year or settings.scrape_from_year, to_year=to_year or settings.scrape_to_year).run()


if __name__ == "__main__":
    asyncio.run(scrape_all())
