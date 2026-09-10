from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.middleware.api_key_auth import AuthContext, get_api_user
from app.schemas.indicator import IndicatorListResponse, IndicatorOut
from app.services import data_service as svc
from app.utils.indicators_seed import CATEGORIES

router = APIRouter()


@router.get("", response_model=IndicatorListResponse, summary="List available indicators")
def list_indicators(
    category: str | None = Query(None, description="economy | demographics | health | education | infrastructure | finance"),
    db: Session = Depends(get_db),
    _: AuthContext = Depends(get_api_user),
):
    rows = svc.list_indicators(db, category=category)
    return IndicatorListResponse(data=[IndicatorOut.model_validate(i) for i in rows], total=len(rows), categories=CATEGORIES)


@router.get("/{code}", response_model=IndicatorOut, summary="Get one indicator definition")
def get_indicator(code: str, db: Session = Depends(get_db), _: AuthContext = Depends(get_api_user)):
    return IndicatorOut.model_validate(svc.get_indicator(db, code))
