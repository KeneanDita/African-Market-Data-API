from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.middleware.api_key_auth import AuthContext, get_api_user
from app.schemas.country import CountryBrief
from app.schemas.data_point import DataPointOut, SeriesResponse, SnapshotItem, SnapshotResponse
from app.schemas.indicator import IndicatorBrief
from app.services import data_service as svc

router = APIRouter()


@router.get("/{iso2}", response_model=SnapshotResponse, summary="Country snapshot: latest value of every indicator")
def country_snapshot(
    iso2: str,
    category: str | None = Query(None, description="Restrict to one category"),
    db: Session = Depends(get_db),
    _: AuthContext = Depends(get_api_user),
):
    country = svc.get_country(db, iso2)
    rows = svc.get_snapshot(db, country, category)
    return SnapshotResponse(
        country=CountryBrief.model_validate(country),
        data=[
            SnapshotItem(
                indicator=IndicatorBrief.model_validate(ind),
                category=ind.category,
                year=dp.year,
                value=float(dp.value) if dp.value is not None else None,
                source=dp.source,
            )
            for ind, dp in rows
        ],
        total=len(rows),
    )


@router.get("/{iso2}/{indicator_code}", response_model=SeriesResponse, summary="Time series for one country + indicator")
def country_indicator_series(
    iso2: str,
    indicator_code: str,
    from_year: int | None = Query(None, alias="from", ge=1960, le=2100),
    to_year: int | None = Query(None, alias="to", ge=1960, le=2100),
    latest: bool = Query(False, description="Return only the most recent value"),
    db: Session = Depends(get_db),
    auth: AuthContext = Depends(get_api_user),
):
    country = svc.get_country(db, iso2)
    indicator = svc.get_indicator(db, indicator_code)
    points = svc.get_series(db, country, indicator, from_year, to_year, min_year=auth.min_year)
    valued = [p for p in points if p.value is not None]
    latest_point = valued[-1] if valued else None
    if latest:
        points = [latest_point] if latest_point else []

    return SeriesResponse(
        country=CountryBrief.model_validate(country),
        indicator=IndicatorBrief.model_validate(indicator),
        data=[DataPointOut(year=p.year, value=float(p.value) if p.value is not None else None) for p in points],
        latest=DataPointOut(year=latest_point.year, value=float(latest_point.value)) if latest_point else None,
        count=len(points),
        source=(latest_point.source if latest_point else indicator.source),
        last_updated=max((p.scraped_at for p in points if p.scraped_at), default=None),
    )
