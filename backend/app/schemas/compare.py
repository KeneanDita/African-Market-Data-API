from pydantic import BaseModel

from app.schemas.data_point import DataPointOut
from app.schemas.indicator import IndicatorBrief


class RankedCountryOut(BaseModel):
    iso2: str
    name: str
    value: float | None
    year: int | None
    rank: int


class CompareResponse(BaseModel):
    indicator: IndicatorBrief
    year: int | None
    data: list[RankedCountryOut]
    continental_average: float | None
    continental_total: float | None
    countries_reporting: int
    missing: list[str]


class TrendSeries(BaseModel):
    iso2: str
    name: str
    data: list[DataPointOut]


class TrendResponse(BaseModel):
    indicator: IndicatorBrief
    from_year: int | None
    to_year: int | None
    series: list[TrendSeries]
