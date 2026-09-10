from __future__ import annotations

from typing import Annotated, Optional

import strawberry
from graphql import GraphQLError
from strawberry.types import Info

from app.graphql.types import CompareResult, Country, CountryRanking, DataPoint, Indicator, IndicatorSnapshot, Region, TrendSeries
from app.services import data_service as svc


def _guard(fn, *args, **kwargs):
    try:
        return fn(*args, **kwargs)
    except svc.NotFound as exc:
        raise GraphQLError(str(exc), extensions={"code": "NOT_FOUND"}) from exc
    except svc.BadRequest as exc:
        raise GraphQLError(str(exc), extensions={"code": "BAD_REQUEST"}) from exc


def _auth(info: Info):
    return info.context["auth"]


def countries(info: Info, region: Optional[str] = None) -> list[Country]:
    return [Country.from_model(c) for c in svc.list_countries(info.context["db"], region=region)]


def country(info: Info, iso2: str) -> Optional[Country]:
    try:
        return Country.from_model(svc.get_country(info.context["db"], iso2))
    except svc.NotFound:
        return None


def indicators(info: Info, category: Optional[str] = None) -> list[Indicator]:
    return [Indicator.from_model(i) for i in svc.list_indicators(info.context["db"], category=category)]


def indicator(info: Info, code: str) -> Optional[Indicator]:
    try:
        return Indicator.from_model(svc.get_indicator(info.context["db"], code))
    except svc.NotFound:
        return None


def data(
    info: Info,
    iso2: str,
    indicator: str,
    from_: Annotated[Optional[int], strawberry.argument(name="from")] = None,
    to: Optional[int] = None,
) -> list[DataPoint]:
    db = info.context["db"]
    auth = _auth(info)
    c = _guard(svc.get_country, db, iso2)
    ind = _guard(svc.get_indicator, db, indicator)
    points = svc.get_series(db, c, ind, from_, to, min_year=auth.min_year if auth else None)
    return [DataPoint.from_model(p, ind) for p in points]


def compare(info: Info, countries: list[str], indicator: str, year: Optional[int] = None) -> CompareResult:
    auth = _auth(info)
    iso2_list = [c.strip().upper() for c in countries if c.strip()]
    result = _guard(svc.compare, info.context["db"], iso2_list, indicator, year, auth.max_compare if auth else 5)
    return CompareResult(
        indicator=Indicator.from_model(result.indicator),
        year=result.year,
        rankings=[CountryRanking(country=Country.from_model(r.country), value=r.value, year=r.year, rank=r.rank) for r in result.rankings],
        continental_average=result.continental_average,
        continental_total=result.continental_total,
        countries_reporting=result.countries_reporting,
        missing=result.missing,
    )


def compare_trend(
    info: Info,
    countries: list[str],
    indicator: str,
    from_: Annotated[Optional[int], strawberry.argument(name="from")] = None,
    to: Optional[int] = None,
) -> list[TrendSeries]:
    db = info.context["db"]
    auth = _auth(info)
    iso2_list = [c.strip().upper() for c in countries if c.strip()]
    result = _guard(svc.compare_trend, db, iso2_list, indicator, from_, to, auth.max_compare if auth else 5, auth.min_year if auth else None)
    models = {c.iso2: c for c in svc.get_countries_by_iso2(db, iso2_list)}
    ind = result["indicator"]
    return [
        TrendSeries(
            country=Country.from_model(models[s["iso2"]]),
            data=[DataPoint(year=p["year"], value=p["value"], source=ind.source, indicator=None) for p in s["data"]],
        )
        for s in result["series"]
    ]


def regions(info: Info) -> list[Region]:
    return [
        Region(name=r["name"], slug=r["slug"], country_count=r["country_count"], population=r["population"], countries=[Country.from_model(c) for c in r["countries"]])
        for r in svc.list_regions(info.context["db"])
    ]


def region_summary(info: Info, region: str, category: Optional[str] = None) -> list[IndicatorSnapshot]:
    result = _guard(svc.region_summary, info.context["db"], region, category)
    return [
        IndicatorSnapshot(indicator=Indicator.from_model(s["indicator"]), value=s["value"], year=s["year"], countries_reporting=s["countries_reporting"])
        for s in result["indicators"]
    ]
