from pydantic import BaseModel, ConfigDict


class IndicatorOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    code: str
    name: str
    category: str
    subcategory: str | None = None
    unit: str | None = None
    aggregation: str
    source: str | None = None
    source_code: str | None = None
    description: str | None = None


class IndicatorBrief(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    code: str
    name: str
    unit: str | None = None


class IndicatorListResponse(BaseModel):
    data: list[IndicatorOut]
    total: int
    categories: list[str]
