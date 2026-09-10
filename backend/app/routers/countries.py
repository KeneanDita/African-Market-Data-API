from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.middleware.api_key_auth import AuthContext, get_api_user
from app.schemas.country import CountryListMeta, CountryListResponse, CountryOut
from app.services import data_service as svc

router = APIRouter()


@router.get("", response_model=CountryListResponse, summary="List all 54 African countries")
def list_countries(
    region: str | None = Query(None, description="Filter by region, e.g. 'East Africa'"),
    sort: str | None = Query(None, description="name | population | area_km2 | iso2 | region"),
    order: str = Query("asc", pattern="^(asc|desc)$"),
    db: Session = Depends(get_db),
    _: AuthContext = Depends(get_api_user),
):
    rows = svc.list_countries(db, region=region, sort=sort, order=order)
    return CountryListResponse(
        data=[CountryOut.model_validate(c) for c in rows],
        total=len(rows),
        meta=CountryListMeta(region_filter=region, sort=sort, order=order),
    )


@router.get("/{iso2}", response_model=CountryOut, summary="Get one country's profile")
def get_country(iso2: str, db: Session = Depends(get_db), _: AuthContext = Depends(get_api_user)):
    return CountryOut.model_validate(svc.get_country(db, iso2))
