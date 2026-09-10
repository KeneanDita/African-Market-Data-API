import time
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.middleware.api_key_auth import AuthContext, get_api_user, invalidate_auth_cache
from app.models.api_user import TIER_LIMITS, ApiUser
from app.models.request_log import RequestLog
from app.schemas.auth import MeResponse, RegisterRequest, RegisterResponse, RotateResponse
from app.utils.cache import get_cache
from app.utils.security import generate_api_key, hash_api_key, key_prefix

router = APIRouter()


@router.post("/register", response_model=RegisterResponse, status_code=201, summary="Register for a free API key")
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    email = payload.email.lower()
    if db.query(ApiUser).filter(ApiUser.email == email).first():
        raise HTTPException(status_code=409, detail="An API key already exists for this email. Contact support to rotate it.")

    raw_key = generate_api_key()
    user = ApiUser(
        email=email,
        name=payload.name,
        api_key_hash=hash_api_key(raw_key),
        key_prefix=key_prefix(raw_key),
        tier="free",
        rate_limit=TIER_LIMITS["free"],
    )
    db.add(user)
    db.commit()

    return RegisterResponse(
        api_key=raw_key,
        tier="free",
        rate_limit=f"{TIER_LIMITS['free']} requests/hour",
        docs=settings.docs_url,
        message="Store this key securely - it cannot be retrieved again. Send it in the X-API-Key header.",
    )


@router.get("/me", response_model=MeResponse, summary="Your account and current-hour usage")
def me(db: Session = Depends(get_db), auth: AuthContext = Depends(get_api_user)):
    user = db.query(ApiUser).filter(ApiUser.api_key_hash == auth.key_hash).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid API key")

    window = int(time.time()) // 3600
    used = get_cache().get(f"ratelimit:{auth.key_hash}:{window}")
    if used is None:
        since = datetime.now(timezone.utc) - timedelta(hours=1)
        used = db.query(func.count(RequestLog.id)).filter(RequestLog.api_key_hash == auth.key_hash, RequestLog.created_at >= since).scalar() or 0
    used = int(used)

    return MeResponse(
        email=user.email,
        name=user.name,
        key_prefix=user.key_prefix,
        tier=user.tier,
        rate_limit=user.rate_limit,
        requests_this_hour=used,
        requests_remaining=max(0, user.rate_limit - used),
        created_at=user.created_at,
        last_seen_at=user.last_seen_at,
    )


@router.post("/rotate", response_model=RotateResponse, summary="Replace your API key with a new one")
def rotate(db: Session = Depends(get_db), auth: AuthContext = Depends(get_api_user)):
    """The old key stops working immediately. Tier and usage history carry over."""
    user = db.query(ApiUser).filter(ApiUser.api_key_hash == auth.key_hash).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid API key")
    old_hash = user.api_key_hash
    raw_key = generate_api_key()
    user.api_key_hash = hash_api_key(raw_key)
    user.key_prefix = key_prefix(raw_key)
    db.commit()
    invalidate_auth_cache(old_hash)
    return RotateResponse(
        api_key=raw_key,
        key_prefix=user.key_prefix,
        tier=user.tier,
        message="Your previous key has been revoked. Store this one securely - it cannot be retrieved again.",
    )
