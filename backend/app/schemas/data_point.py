from datetime import datetime

from pydantic import BaseModel

from app.schemas.country import CountryBrief
from app.schemas.indicator import IndicatorBrief


class DataPointOut(BaseModel):
    year: int
    value: float | None


class SeriesResponse(BaseModel):
    country: CountryBrief
    indicator: IndicatorBrief
    data: list[DataPointOut]
    latest: DataPointOut | None
    count: int
    source: str | None
    last_updated: datetime | None


class SnapshotItem(BaseModel):
    indicator: IndicatorBrief
    category: str
    year: int
    value: float | None
    source: str | None


class SnapshotResponse(BaseModel):
    country: CountryBrief
    data: list[SnapshotItem]
    total: int
