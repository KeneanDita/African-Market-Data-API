from pydantic import BaseModel, ConfigDict


class CountryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    iso2: str
    iso3: str
    name: str
    region: str | None = None
    capital: str | None = None
    currency: str | None = None
    currency_code: str | None = None
    population: int | None = None
    area_km2: int | None = None
    languages: list[str] | None = None


class CountryBrief(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    iso2: str
    name: str


class CountryListMeta(BaseModel):
    region_filter: str | None = None
    sort: str | None = None
    order: str = "asc"


class CountryListResponse(BaseModel):
    data: list[CountryOut]
    total: int
    meta: CountryListMeta
