"""Cache abstraction: Redis when configured and reachable, otherwise an in-process fallback.

The in-memory backend is fine for local development and tests. Rate limits and cached
responses are per-process in that mode, so use Redis for anything multi-instance.
"""

from __future__ import annotations

import json
import logging
import threading
import time
from typing import Any

from app.config import settings

logger = logging.getLogger(__name__)


class BaseCache:
    backend = "base"

    def get(self, key: str) -> str | None:
        raise NotImplementedError

    def set(self, key: str, value: str, ttl: int | None = None) -> None:
        raise NotImplementedError

    def delete(self, key: str) -> None:
        raise NotImplementedError

    def incr(self, key: str, ttl: int | None = None) -> int:
        """Atomically increment; sets `ttl` when the key is first created."""
        raise NotImplementedError

    def get_json(self, key: str) -> Any | None:
        raw = self.get(key)
        return json.loads(raw) if raw is not None else None

    def set_json(self, key: str, value: Any, ttl: int | None = None) -> None:
        self.set(key, json.dumps(value, default=str), ttl)


class MemoryCache(BaseCache):
    backend = "memory"

    def __init__(self) -> None:
        self._store: dict[str, tuple[str | int, float | None]] = {}
        self._lock = threading.Lock()

    def _purge(self, key: str) -> None:
        item = self._store.get(key)
        if item and item[1] is not None and item[1] <= time.time():
            del self._store[key]

    def get(self, key: str) -> str | None:
        with self._lock:
            self._purge(key)
            item = self._store.get(key)
            return None if item is None else str(item[0])

    def set(self, key: str, value: str, ttl: int | None = None) -> None:
        with self._lock:
            self._store[key] = (value, time.time() + ttl if ttl else None)

    def delete(self, key: str) -> None:
        with self._lock:
            self._store.pop(key, None)

    def incr(self, key: str, ttl: int | None = None) -> int:
        with self._lock:
            self._purge(key)
            item = self._store.get(key)
            if item is None:
                self._store[key] = (1, time.time() + ttl if ttl else None)
                return 1
            new_val = int(item[0]) + 1
            self._store[key] = (new_val, item[1])
            return new_val

    def clear(self) -> None:
        with self._lock:
            self._store.clear()


class RedisCache(BaseCache):
    backend = "redis"

    def __init__(self, url: str) -> None:
        import redis

        self._r = redis.from_url(url, decode_responses=True, socket_connect_timeout=2, socket_timeout=2)
        self._r.ping()

    def get(self, key: str) -> str | None:
        return self._r.get(key)

    def set(self, key: str, value: str, ttl: int | None = None) -> None:
        self._r.set(key, value, ex=ttl)

    def delete(self, key: str) -> None:
        self._r.delete(key)

    def incr(self, key: str, ttl: int | None = None) -> int:
        pipe = self._r.pipeline()
        pipe.incr(key)
        if ttl:
            pipe.expire(key, ttl, nx=True)
        return int(pipe.execute()[0])


_cache: BaseCache | None = None
_cache_lock = threading.Lock()


def get_cache() -> BaseCache:
    global _cache
    if _cache is not None:
        return _cache
    with _cache_lock:
        if _cache is not None:
            return _cache
        if settings.redis_url:
            try:
                _cache = RedisCache(settings.redis_url)
                logger.info("Cache backend: redis")
                return _cache
            except Exception as exc:  # noqa: BLE001
                logger.warning("Redis unavailable (%s); falling back to in-memory cache", exc)
        _cache = MemoryCache()
        logger.info("Cache backend: memory")
        return _cache


def reset_cache() -> None:
    """Used by tests to drop the singleton."""
    global _cache
    _cache = None
