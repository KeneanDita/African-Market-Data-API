"""Caches successful JSON GET responses for read-heavy data endpoints (1h TTL by default).

Cache key includes the caller's tier because free/pro see different historical ranges.
"""

from __future__ import annotations

import hashlib

from fastapi import Request
from fastapi.responses import Response
from starlette.middleware.base import BaseHTTPMiddleware

from app.config import settings
from app.utils.cache import get_cache

CACHEABLE_PREFIXES = ("/v1/data", "/v1/compare", "/v1/regions", "/v1/countries", "/v1/indicators")


class ResponseCacheMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.method != "GET" or not request.url.path.startswith(CACHEABLE_PREFIXES):
            return await call_next(request)

        auth = getattr(request.state, "auth", None)
        tier = auth.tier if auth else "anon"
        raw_key = f"{tier}|{request.url.path}?{request.url.query}"
        key = "resp:" + hashlib.sha1(raw_key.encode()).hexdigest()

        cache = get_cache()
        hit = cache.get_json(key)
        if hit:
            return Response(content=hit["body"], status_code=200, media_type="application/json", headers={"X-Cache": "HIT"})

        response = await call_next(request)
        if response.status_code != 200 or "application/json" not in response.headers.get("content-type", ""):
            response.headers["X-Cache"] = "BYPASS"
            return response

        body = b"".join([chunk async for chunk in response.body_iterator])
        cache.set_json(key, {"body": body.decode("utf-8")}, ttl=settings.cache_ttl_seconds)
        headers = {k: v for k, v in response.headers.items() if k.lower() not in ("content-length",)}
        headers["X-Cache"] = "MISS"
        return Response(content=body, status_code=200, media_type="application/json", headers=headers)


def invalidate_response_cache() -> None:
    """Best-effort: memory backend can be cleared wholesale; Redis relies on TTL expiry."""
    cache = get_cache()
    if hasattr(cache, "clear"):
        cache.clear()
