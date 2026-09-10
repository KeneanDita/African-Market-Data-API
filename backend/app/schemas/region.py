from pydantic import BaseModel

from app.schemas.country import CountryBrief
from app.schemas.indicator import IndicatorBrief


class RegionOut(BaseModel):
    name: str
    slug: str
    country_count: int
    population: int | None
    countries: list[CountryBrief]


class RegionListResponse(BaseModel):
    data: list[RegionOut]
    total: int


class RegionIndicatorSummary(BaseModel):
    indicator: IndicatorBrief
    category: str
    value: float | None
    aggregation: str
    year: int | None
    countries_reporting: int


class RegionSummaryResponse(BaseModel):
    region: str
    country_count: int
    countries: list[CountryBrief]
    indicators: list[RegionIndicatorSummary]
