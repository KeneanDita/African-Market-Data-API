"""API-key authentication.

`authenticate()` is used by the rate-limiter middleware (which runs first and stores the result on
`request.state`) and `get_api_user()` is the FastAPI dependency routers use to read tier information.
Resolved keys are cached briefly so the hot path doesn't hit the database on every request.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass

from fastapi import Depends, HTTPException, Request
from fastapi.security import APIKeyHeader
from sqlalchemy.orm import Session

from app.config import settings
from app.database import SessionLocal, get_db
from app.models.api_user import TIER_LIMITS, TIER_MAX_COMPARE, TIER_MIN_YEAR, ApiUser
from app.utils.cache import get_cache
from app.utils.security import hash_api_key

PUBLIC_PATHS = {"/", "/health", "/docs", "/redoc", "/openapi.json", "/v1/auth/register"}
# /v1/admin has its own token check and must not consume API-key rate budgets.
PUBLIC_PREFIXES = ("/static", "/v1/admin")

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False, description="Get a free key at POST /v1/auth/register")

AUTH_CACHE_TTL = 300


@dataclass
class AuthContext:
    user_id: str
    email: str
    tier: str
    rate_limit: int
    key_hash: str

    @property
    def max_compare(self) -> int:
        return TIER_MAX_COMPARE.get(self.tier, TIER_MAX_COMPARE["free"])

    @property
    def min_year(self) -> int:
        return TIER_MIN_YEAR.get(self.tier, TIER_MIN_YEAR["free"])


def is_public_path(path: str, method: str = "GET") -> bool:
    if path in PUBLIC_PATHS or path.startswith(PUBLIC_PREFIXES):
        return True
    # GraphiQL playground page is public; GraphQL queries (POST) are not.
    if path.rstrip("/") == "/graphql" and method == "GET":
        return True
    return False


def authenticate(api_key: str | None, db: Session | None = None) -> AuthContext | None:
    if not api_key:
        return None
    key_hash = hash_api_key(api_key)
    cache = get_cache()
    cached = cache.get_json(f"auth:{key_hash}")
    if cached:
        return AuthContext(**cached)

    own_session = db is None
    session = db or SessionLocal()
    try:
        user = session.query(ApiUser).filter(ApiUser.api_key_hash == key_hash).first()
    finally:
        if own_session:
            session.close()
    if not user:
        return None
    ctx = AuthContext(
        user_id=str(user.id),
        email=user.email,
        tier=user.tier,
        rate_limit=user.rate_limit or TIER_LIMITS.get(user.tier, TIER_LIMITS["free"]),
        key_hash=key_hash,
    )
    cache.set_json(f"auth:{key_hash}", asdict(ctx), AUTH_CACHE_TTL)
    return ctx


def invalidate_auth_cache(key_hash: str) -> None:
    get_cache().delete(f"auth:{key_hash}")


def unauthorized_detail() -> dict:
    return {
        "error": "API key required",
        "hint": "Send your key in the X-API-Key header. Register for a free key at POST /v1/auth/register.",
        "docs": settings.docs_url,
    }


def get_api_user(
    request: Request,
    api_key: str | None = Depends(api_key_header),
    db: Session = Depends(get_db),
) -> AuthContext:
    """Dependency: returns the caller's auth context or raises 401."""
    ctx: AuthContext | None = getattr(request.state, "auth", None)
    if ctx is None:
        ctx = authenticate(api_key, db)
        if ctx is None and not settings.require_api_key:
            ctx = AuthContext(user_id="anonymous", email="", tier="free", rate_limit=TIER_LIMITS["free"], key_hash="anonymous")
    if ctx is None:
        raise HTTPException(status_code=401, detail=unauthorized_detail())
    request.state.auth = ctx
    return ctx
