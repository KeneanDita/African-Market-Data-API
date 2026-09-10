from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.middleware.api_key_auth import AuthContext, get_api_user
from app.schemas.country import CountryBrief
from app.schemas.indicator import IndicatorBrief
from app.schemas.region import RegionIndicatorSummary, RegionListResponse, RegionOut, RegionSummaryResponse
from app.services import data_service as svc

router = APIRouter()


@router.get("", response_model=RegionListResponse, summary="Africa's five regions and their members")
def list_regions(db: Session = Depends(get_db), _: AuthContext = Depends(get_api_user)):
    regions = svc.list_regions(db)
    return RegionListResponse(
        data=[
            RegionOut(
                name=r["name"],
                slug=r["slug"],
                country_count=r["country_count"],
                population=r["population"],
                countries=[CountryBrief.model_validate(c) for c in r["countries"]],
            )
            for r in regions
        ],
        total=len(regions),
    )


@router.get("/{region}/summary", response_model=RegionSummaryResponse, summary="Aggregated indicators for a region")
def region_summary(
    region: str,
    category: str | None = Query(None),
    db: Session = Depends(get_db),
    _: AuthContext = Depends(get_api_user),
):
    result = svc.region_summary(db, region, category)
    return RegionSummaryResponse(
        region=result["region"],
        country_count=result["country_count"],
        countries=[CountryBrief.model_validate(c) for c in result["countries"]],
        indicators=[
            RegionIndicatorSummary(
                indicator=IndicatorBrief.model_validate(s["indicator"]),
                category=s["indicator"].category,
                value=s["value"],
                aggregation=s["aggregation"],
                year=s["year"],
                countries_reporting=s["countries_reporting"],
            )
            for s in result["indicators"]
        ],
    )
