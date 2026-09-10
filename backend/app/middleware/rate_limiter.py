"""Fixed-window (per hour) rate limiting keyed on the hashed API key.

Runs before the routers: authenticates the key, stores the context on `request.state.auth`
and rejects with 429 when the tier's hourly budget is exhausted.
"""

from __future__ import annotations

import time

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.config import settings
from app.middleware.api_key_auth import AuthContext, authenticate, is_public_path, unauthorized_detail
from app.models.api_user import TIER_LIMITS
from app.utils.cache import get_cache

WINDOW_SECONDS = 3600


class RateLimiterMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        path = request.url.path
        if request.method == "OPTIONS" or is_public_path(path, request.method):
            return await call_next(request)

        api_key = request.headers.get("X-API-Key")
        ctx = authenticate(api_key)
        if ctx is None:
            if settings.require_api_key:
                return JSONResponse(status_code=401, content={"detail": unauthorized_detail()}, headers={"WWW-Authenticate": "ApiKey"})
            ctx = AuthContext(user_id="anonymous", email="", tier="free", rate_limit=TIER_LIMITS["free"], key_hash="anon:" + (request.client.host if request.client else "unknown"))
        request.state.auth = ctx

        cache = get_cache()
        now = int(time.time())
        window = now // WINDOW_SECONDS
        reset_in = WINDOW_SECONDS - (now % WINDOW_SECONDS)
        current = cache.incr(f"ratelimit:{ctx.key_hash}:{window}", ttl=WINDOW_SECONDS)
        limit = ctx.rate_limit

        if current > limit:
            return JSONResponse(
                status_code=429,
                content={
                    "detail": {
                        "error": "Rate limit exceeded",
                        "limit": limit,
                        "tier": ctx.tier,
                        "reset_in_seconds": reset_in,
                        "upgrade": "https://africadata.dev/pricing",
                    }
                },
                headers={
                    "Retry-After": str(reset_in),
                    "X-RateLimit-Limit": str(limit),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(reset_in),
                },
            )

        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(limit)
        response.headers["X-RateLimit-Remaining"] = str(max(0, limit - current))
        response.headers["X-RateLimit-Reset"] = str(reset_in)
        return response
