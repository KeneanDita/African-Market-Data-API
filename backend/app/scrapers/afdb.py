"""African Development Bank data portal.

The AfDB portal (dataportal.opendataforafrica.org) exposes a Knoema-style API that needs a
registered app key, and its dataset ids change between releases. This scraper is a documented
extension point: implement `fetch()` against the dataset you have access to and map rows to
`Observation`s; `INSURANCE_PENETRATION` is the indicator currently attributed to this source.
"""

from __future__ import annotations

import asyncio
import logging

import httpx

from app.scrapers.base import BaseScraper

logger = logging.getLogger(__name__)


class AfDBScraper(BaseScraper):
    source = "African Development Bank"

    async def scrape(self, client: httpx.AsyncClient) -> None:  # noqa: ARG002
        indicators = self.indicators_for_source()
        logger.warning(
            "[AfDB] no public machine-readable feed configured; %d indicator(s) attributed to AfDB left untouched: %s",
            len(indicators),
            ", ".join(indicators) or "-",
        )


async def scrape_all(from_year: int | None = None, to_year: int | None = None):
    from app.config import settings

    return await AfDBScraper(from_year=from_year or settings.scrape_from_year, to_year=to_year or settings.scrape_to_year).run()


if __name__ == "__main__":
    asyncio.run(scrape_all())
