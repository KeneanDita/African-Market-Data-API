"""Scraper tests run fully offline against mocked upstream payloads."""

from decimal import Decimal

import httpx
import pytest

from app.models.country import Country
from app.models.data_point import DataPoint
from app.models.indicator import Indicator
from app.scrapers.imf import IMFScraper
from app.scrapers.world_bank import WorldBankScraper


def _wb_payload(rows):
    return [{"page": 1, "pages": 1, "per_page": 20000, "total": len(rows)}, rows]


@pytest.mark.asyncio
async def test_world_bank_scraper_upserts_and_respects_existing(client, db):
    gini = db.query(Indicator).filter_by(code="GINI_INDEX").first()
    literacy = db.query(Indicator).filter_by(code="LITERACY_RATE").first()

    def handler(request: httpx.Request) -> httpx.Response:
        if gini.source_code in request.url.path:
            rows = [
                {"country": {"id": "ET"}, "date": "2015", "value": 35.0},
                {"country": {"id": "ET"}, "date": "2016", "value": None},
                {"country": {"id": "ZZ"}, "date": "2015", "value": 1.0},  # unknown country -> skipped
            ]
        elif literacy.source_code in request.url.path:
            rows = [{"country": {"id": "KE"}, "date": "2021", "value": 82.6}]
        else:
            rows = []
        return httpx.Response(200, json=_wb_payload(rows))

    scraper = WorldBankScraper(db=db, from_year=2000, to_year=2025, only_codes=["GINI_INDEX", "LITERACY_RATE"])
    scraper.http_client = lambda: httpx.AsyncClient(transport=httpx.MockTransport(handler))
    stats = await scraper.run()

    assert stats.inserted == 2
    assert stats.fetched == 2  # non-African "ZZ" row filtered out before parsing
    et = db.query(Country).filter_by(iso2="ET").first()
    dp = db.query(DataPoint).filter_by(country_id=et.id, indicator_id=gini.id, year=2015).first()
    assert dp.value == Decimal("35.000000")
    assert dp.source == "World Bank"

    # Second run with a changed value updates in place instead of duplicating.
    def handler2(request: httpx.Request) -> httpx.Response:
        rows = [{"country": {"id": "ET"}, "date": "2015", "value": 35.5}] if gini.source_code in request.url.path else []
        return httpx.Response(200, json=_wb_payload(rows))

    scraper2 = WorldBankScraper(db=db, only_codes=["GINI_INDEX"])
    scraper2.http_client = lambda: httpx.AsyncClient(transport=httpx.MockTransport(handler2))
    stats2 = await scraper2.run()
    assert stats2.updated == 1 and stats2.inserted == 0
    db.expire_all()
    assert db.query(DataPoint).filter_by(country_id=et.id, indicator_id=gini.id, year=2015).count() == 1


@pytest.mark.asyncio
async def test_imf_fills_gaps_but_never_overwrites_world_bank(client, db):
    def handler(request: httpx.Request) -> httpx.Response:
        code = request.url.path.rstrip("/").split("/")[-1]
        if code == "GGXWDG_NGDP":
            values = {"ETH": {"2022": 46.4, "2023": 38.9, "2099": 10.0}, "USA": {"2023": 120.0}}  # USA filtered out
        elif code == "PCPIPCH":
            # ET 2023 already has a World Bank value (30.2); 2019 is a gap.
            values = {"ETH": {"2023": 99.9, "2019": 15.8}}
        else:
            values = {}
        return httpx.Response(200, json={"values": {code: values}})

    scraper = IMFScraper(db=db, from_year=2000, to_year=2025)
    scraper.http_client = lambda: httpx.AsyncClient(transport=httpx.MockTransport(handler))
    await scraper.run()

    et = db.query(Country).filter_by(iso2="ET").first()
    debt = db.query(Indicator).filter_by(code="GOVERNMENT_DEBT_GDP").first()
    infl = db.query(Indicator).filter_by(code="INFLATION_ANNUAL").first()
    debt_years = {dp.year for dp in db.query(DataPoint).filter_by(country_id=et.id, indicator_id=debt.id)}
    assert debt_years == {2022, 2023}  # projection year dropped

    db.expire_all()
    wb_2023 = db.query(DataPoint).filter_by(country_id=et.id, indicator_id=infl.id, year=2023).first()
    assert wb_2023.value == Decimal("30.2") and wb_2023.source == "World Bank"
    gap_2019 = db.query(DataPoint).filter_by(country_id=et.id, indicator_id=infl.id, year=2019).first()
    assert gap_2019.source == "IMF"
