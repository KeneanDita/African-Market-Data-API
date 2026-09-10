from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.middleware.api_key_auth import AuthContext, get_api_user
from app.schemas.compare import CompareResponse, RankedCountryOut, TrendResponse, TrendSeries
from app.schemas.data_point import DataPointOut
from app.schemas.indicator import IndicatorBrief
from app.services import data_service as svc
from app.utils.normalizer import clean_iso2_list

router = APIRouter()


@router.get("", response_model=CompareResponse, summary="Rank countries on one indicator")
def compare_countries(
    countries: str = Query(..., description="Comma-separated ISO2 codes, e.g. ET,NG,KE"),
    indicator: str = Query(..., description="Indicator code, e.g. GDP_CURRENT_USD"),
    year: int | None = Query(None, ge=1960, le=2100, description="Defaults to each country's latest value"),
    db: Session = Depends(get_db),
    auth: AuthContext = Depends(get_api_user),
):
    result = svc.compare(db, clean_iso2_list(countries), indicator, year, max_countries=auth.max_compare)
    return CompareResponse(
        indicator=IndicatorBrief.model_validate(result.indicator),
        year=result.year,
        data=[
            RankedCountryOut(iso2=r.country.iso2, name=r.country.name, value=r.value, year=r.year, rank=r.rank)
            for r in result.rankings
        ],
        continental_average=result.continental_average,
        continental_total=result.continental_total,
        countries_reporting=result.countries_reporting,
        missing=result.missing,
    )


@router.get("/trend", response_model=TrendResponse, summary="Compare time-series trends across countries")
def compare_trend(
    countries: str = Query(..., description="Comma-separated ISO2 codes"),
    indicator: str = Query(...),
    from_year: int | None = Query(None, alias="from", ge=1960, le=2100),
    to_year: int | None = Query(None, alias="to", ge=1960, le=2100),
    db: Session = Depends(get_db),
    auth: AuthContext = Depends(get_api_user),
):
    result = svc.compare_trend(
        db, clean_iso2_list(countries), indicator, from_year, to_year, max_countries=auth.max_compare, min_year=auth.min_year
    )
    return TrendResponse(
        indicator=IndicatorBrief.model_validate(result["indicator"]),
        from_year=result["from_year"],
        to_year=result["to_year"],
        series=[
            TrendSeries(iso2=s["iso2"], name=s["name"], data=[DataPointOut(**p) for p in s["data"]])
            for s in result["series"]
        ],
    )
