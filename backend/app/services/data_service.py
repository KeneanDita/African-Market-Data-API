"""Query logic shared by the REST routers and GraphQL resolvers."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.country import Country
from app.models.data_point import DataPoint
from app.models.indicator import Indicator
from app.utils.countries_seed import REGIONS

COUNTRY_SORT_FIELDS = {"name", "population", "area_km2", "iso2", "region"}


class NotFound(Exception):
    pass


class BadRequest(Exception):
    pass


def _f(value: Decimal | None) -> float | None:
    return None if value is None else float(value)


# ---------------------------------------------------------------- countries


def list_countries(db: Session, region: str | None = None, sort: str | None = None, order: str = "asc") -> list[Country]:
    q = db.query(Country)
    if region:
        q = q.filter(func.lower(Country.region) == region.strip().lower())
    sort_field = sort if sort in COUNTRY_SORT_FIELDS else "name"
    col = getattr(Country, sort_field)
    q = q.order_by(col.desc().nullslast() if order == "desc" else col.asc().nullslast())
    return q.all()


def get_country(db: Session, iso2: str) -> Country:
    country = db.query(Country).filter(Country.iso2 == iso2.strip().upper()).first()
    if not country:
        raise NotFound(f"Country '{iso2}' not found. Use an ISO2 code such as ET, NG or KE.")
    return country


def get_countries_by_iso2(db: Session, iso2_list: list[str]) -> list[Country]:
    rows = db.query(Country).filter(Country.iso2.in_(iso2_list)).all()
    by_code = {c.iso2: c for c in rows}
    return [by_code[c] for c in iso2_list if c in by_code]


# ---------------------------------------------------------------- indicators


def list_indicators(db: Session, category: str | None = None) -> list[Indicator]:
    q = db.query(Indicator)
    if category:
        q = q.filter(func.lower(Indicator.category) == category.strip().lower())
    return q.order_by(Indicator.category, Indicator.code).all()


def get_indicator(db: Session, code: str) -> Indicator:
    ind = db.query(Indicator).filter(Indicator.code == code.strip().upper()).first()
    if not ind:
        raise NotFound(f"Indicator '{code}' not found. See /v1/indicators for the full list.")
    return ind


# ---------------------------------------------------------------- series


def get_series(
    db: Session,
    country: Country,
    indicator: Indicator,
    from_year: int | None = None,
    to_year: int | None = None,
    min_year: int | None = None,
) -> list[DataPoint]:
    q = db.query(DataPoint).filter(DataPoint.country_id == country.id, DataPoint.indicator_id == indicator.id)
    floor = max([y for y in (from_year, min_year) if y is not None], default=None)
    if floor is not None:
        q = q.filter(DataPoint.year >= floor)
    if to_year is not None:
        q = q.filter(DataPoint.year <= to_year)
    return q.order_by(DataPoint.year.asc()).all()


def get_latest_point(db: Session, country_id: int, indicator_id: int, year: int | None = None) -> DataPoint | None:
    q = db.query(DataPoint).filter(
        DataPoint.country_id == country_id,
        DataPoint.indicator_id == indicator_id,
        DataPoint.value.isnot(None),
    )
    if year is not None:
        return q.filter(DataPoint.year == year).first()
    return q.order_by(DataPoint.year.desc()).first()


def get_snapshot(db: Session, country: Country, category: str | None = None) -> list[tuple[Indicator, DataPoint]]:
    """Latest non-null value for every indicator that has data for this country."""
    latest_year = (
        select(DataPoint.indicator_id, func.max(DataPoint.year).label("year"))
        .where(DataPoint.country_id == country.id, DataPoint.value.isnot(None))
        .group_by(DataPoint.indicator_id)
        .subquery()
    )
    q = (
        db.query(Indicator, DataPoint)
        .join(DataPoint, DataPoint.indicator_id == Indicator.id)
        .join(latest_year, (latest_year.c.indicator_id == DataPoint.indicator_id) & (latest_year.c.year == DataPoint.year))
        .filter(DataPoint.country_id == country.id)
    )
    if category:
        q = q.filter(func.lower(Indicator.category) == category.strip().lower())
    return q.order_by(Indicator.category, Indicator.code).all()


def _latest_per_country(db: Session, indicator_id: int, year: int | None) -> dict[int, DataPoint]:
    """Map country_id -> data point for a given year, or the latest available per country."""
    q = db.query(DataPoint).filter(DataPoint.indicator_id == indicator_id, DataPoint.value.isnot(None))
    if year is not None:
        return {dp.country_id: dp for dp in q.filter(DataPoint.year == year).all()}
    latest = (
        select(DataPoint.country_id, func.max(DataPoint.year).label("year"))
        .where(DataPoint.indicator_id == indicator_id, DataPoint.value.isnot(None))
        .group_by(DataPoint.country_id)
        .subquery()
    )
    rows = (
        db.query(DataPoint)
        .join(latest, (latest.c.country_id == DataPoint.country_id) & (latest.c.year == DataPoint.year))
        .filter(DataPoint.indicator_id == indicator_id)
        .all()
    )
    return {dp.country_id: dp for dp in rows}


# ---------------------------------------------------------------- compare


@dataclass
class RankedCountry:
    country: Country
    value: float | None
    year: int | None
    rank: int


@dataclass
class CompareResult:
    indicator: Indicator
    year: int | None
    rankings: list[RankedCountry]
    continental_average: float | None
    continental_total: float | None
    countries_reporting: int
    missing: list[str]


def compare(db: Session, iso2_list: list[str], indicator_code: str, year: int | None, max_countries: int) -> CompareResult:
    if not iso2_list:
        raise BadRequest("Provide at least one ISO2 country code.")
    if len(iso2_list) > max_countries:
        raise BadRequest(f"Maximum {max_countries} countries per comparison on your tier.")
    indicator = get_indicator(db, indicator_code)
    countries = get_countries_by_iso2(db, iso2_list)
    unknown = sorted(set(iso2_list) - {c.iso2 for c in countries})
    if unknown:
        raise NotFound(f"Unknown country code(s): {', '.join(unknown)}")

    per_country = _latest_per_country(db, indicator.id, year)

    ranked: list[RankedCountry] = []
    missing: list[str] = []
    for c in countries:
        dp = per_country.get(c.id)
        if dp is None:
            missing.append(c.iso2)
            continue
        ranked.append(RankedCountry(country=c, value=_f(dp.value), year=dp.year, rank=0))
    ranked.sort(key=lambda r: r.value if r.value is not None else float("-inf"), reverse=True)
    for i, r in enumerate(ranked, start=1):
        r.rank = i

    # Continental stats use every African country with data, not only the ones being compared.
    all_values = [float(dp.value) for dp in per_country.values() if dp.value is not None]
    total = sum(all_values) if all_values else None
    avg = total / len(all_values) if all_values else None
    resolved_year = year if year is not None else (max((r.year for r in ranked if r.year), default=None))

    return CompareResult(
        indicator=indicator,
        year=resolved_year,
        rankings=ranked,
        continental_average=avg,
        continental_total=total if indicator.aggregation == "sum" else None,
        countries_reporting=len(all_values),
        missing=missing,
    )


def compare_trend(
    db: Session,
    iso2_list: list[str],
    indicator_code: str,
    from_year: int | None,
    to_year: int | None,
    max_countries: int,
    min_year: int | None = None,
) -> dict:
    if not iso2_list:
        raise BadRequest("Provide at least one ISO2 country code.")
    if len(iso2_list) > max_countries:
        raise BadRequest(f"Maximum {max_countries} countries per comparison on your tier.")
    indicator = get_indicator(db, indicator_code)
    countries = get_countries_by_iso2(db, iso2_list)
    unknown = sorted(set(iso2_list) - {c.iso2 for c in countries})
    if unknown:
        raise NotFound(f"Unknown country code(s): {', '.join(unknown)}")

    series = []
    years: set[int] = set()
    for c in countries:
        points = get_series(db, c, indicator, from_year, to_year, min_year)
        years.update(p.year for p in points)
        series.append({
            "iso2": c.iso2,
            "name": c.name,
            "data": [{"year": p.year, "value": _f(p.value)} for p in points],
        })
    return {
        "indicator": indicator,
        "from_year": min(years) if years else from_year,
        "to_year": max(years) if years else to_year,
        "series": series,
    }


# ---------------------------------------------------------------- regions


def list_regions(db: Session) -> list[dict]:
    countries = db.query(Country).order_by(Country.name).all()
    out = []
    for region in REGIONS:
        members = [c for c in countries if c.region == region]
        pop = sum(c.population for c in members if c.population) or None
        out.append({
            "name": region,
            "slug": region.lower().replace(" ", "-"),
            "country_count": len(members),
            "population": pop,
            "countries": members,
        })
    return out


def resolve_region(name: str) -> str:
    wanted = name.strip().lower().replace("-", " ").replace("_", " ")
    for region in REGIONS:
        if region.lower() == wanted or region.lower().split()[0] == wanted:
            return region
    raise NotFound(f"Region '{name}' not found. Valid regions: {', '.join(REGIONS)}")


def region_summary(db: Session, region_name: str, category: str | None = None) -> dict:
    region = resolve_region(region_name)
    members = db.query(Country).filter(Country.region == region).all()
    member_ids = {c.id for c in members}
    indicators = list_indicators(db, category)

    summaries = []
    for ind in indicators:
        per_country = _latest_per_country(db, ind.id, None)
        points = [dp for cid, dp in per_country.items() if cid in member_ids and dp.value is not None]
        if not points:
            continue
        values = [float(dp.value) for dp in points]
        value = sum(values) if ind.aggregation == "sum" else sum(values) / len(values)
        summaries.append({
            "indicator": ind,
            "value": value,
            "aggregation": ind.aggregation,
            "year": max(dp.year for dp in points),
            "countries_reporting": len(points),
        })
    return {"region": region, "country_count": len(members), "countries": members, "indicators": summaries}
