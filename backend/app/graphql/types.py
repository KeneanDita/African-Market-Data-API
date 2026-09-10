from __future__ import annotations

from typing import Annotated, Optional

import strawberry
from strawberry.types import Info

from app.models.country import Country as CountryModel
from app.models.data_point import DataPoint as DataPointModel
from app.models.indicator import Indicator as IndicatorModel
from app.services import data_service as svc


def _f(value) -> Optional[float]:
    return None if value is None else float(value)


@strawberry.type
class Indicator:
    code: str
    name: str
    category: str
    subcategory: Optional[str]
    unit: Optional[str]
    description: Optional[str]
    source: Optional[str]
    aggregation: str

    @classmethod
    def from_model(cls, m: IndicatorModel) -> "Indicator":
        return cls(
            code=m.code, name=m.name, category=m.category, subcategory=m.subcategory, unit=m.unit,
            description=m.description, source=m.source, aggregation=m.aggregation,
        )


@strawberry.type
class DataPoint:
    year: int
    value: Optional[float]
    source: Optional[str]
    indicator: Optional[Indicator]

    @classmethod
    def from_model(cls, m: DataPointModel, indicator: IndicatorModel | None = None) -> "DataPoint":
        return cls(year=m.year, value=_f(m.value), source=m.source, indicator=Indicator.from_model(indicator) if indicator else None)


@strawberry.type
class IndicatorSnapshot:
    indicator: Indicator
    value: Optional[float]
    year: Optional[int]
    countries_reporting: Optional[int] = None


@strawberry.type
class Country:
    _id: strawberry.Private[int]
    iso2: str
    iso3: str
    name: str
    region: Optional[str]
    capital: Optional[str]
    currency: Optional[str]
    currency_code: Optional[str]
    population: Optional[int]
    area_km2: Optional[int]
    languages: Optional[list[str]]

    @classmethod
    def from_model(cls, m: CountryModel) -> "Country":
        return cls(
            _id=m.id, iso2=m.iso2, iso3=m.iso3, name=m.name, region=m.region, capital=m.capital,
            currency=m.currency, currency_code=m.currency_code, population=m.population,
            area_km2=m.area_km2, languages=m.languages,
        )

    @strawberry.field(description="Time series for one indicator on this country")
    def data_points(
        self,
        info: Info,
        indicator: str,
        from_: Annotated[Optional[int], strawberry.argument(name="from")] = None,
        to: Optional[int] = None,
    ) -> list[DataPoint]:
        db = info.context["db"]
        auth = info.context["auth"]
        country = svc.get_country(db, self.iso2)
        ind = svc.get_indicator(db, indicator)
        points = svc.get_series(db, country, ind, from_, to, min_year=auth.min_year if auth else None)
        return [DataPoint.from_model(p, ind) for p in points]

    @strawberry.field(description="Latest value of every indicator for this country")
    def latest_snapshot(self, info: Info, category: Optional[str] = None) -> list[IndicatorSnapshot]:
        db = info.context["db"]
        country = svc.get_country(db, self.iso2)
        return [
            IndicatorSnapshot(indicator=Indicator.from_model(ind), value=_f(dp.value), year=dp.year)
            for ind, dp in svc.get_snapshot(db, country, category)
        ]


@strawberry.type
class CountryRanking:
    country: Country
    value: Optional[float]
    year: Optional[int]
    rank: int


@strawberry.type
class CompareResult:
    indicator: Indicator
    year: Optional[int]
    rankings: list[CountryRanking]
    continental_average: Optional[float]
    continental_total: Optional[float]
    countries_reporting: int
    missing: list[str]


@strawberry.type
class TrendSeries:
    country: Country
    data: list[DataPoint]


@strawberry.type
class Region:
    name: str
    slug: str
    country_count: int
    population: Optional[int]
    countries: list[Country]
