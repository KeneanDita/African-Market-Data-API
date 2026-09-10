from decimal import Decimal

import pytest

from app.middleware.api_key_auth import invalidate_auth_cache
from app.models.api_user import ApiUser
from app.utils.cache import MemoryCache
from app.utils.normalizer import clean_iso2_list, parse_number, parse_year


def test_rate_limit_enforced(client, db):
    resp = client.post("/v1/auth/register", json={"email": "limited@example.com"})
    key = resp.json()["api_key"]
    user = db.query(ApiUser).filter(ApiUser.email == "limited@example.com").first()
    user.rate_limit = 3
    db.commit()
    invalidate_auth_cache(user.api_key_hash)

    headers = {"X-API-Key": key}
    for i in range(3):
        r = client.get("/v1/countries/ET", headers=headers)
        assert r.status_code == 200
        assert r.headers["X-RateLimit-Remaining"] == str(2 - i)
    blocked = client.get("/v1/countries/ET", headers=headers)
    assert blocked.status_code == 429
    assert blocked.json()["detail"]["error"] == "Rate limit exceeded"
    assert "Retry-After" in blocked.headers


def test_memory_cache_incr_and_ttl(monkeypatch):
    c = MemoryCache()
    assert c.incr("k", ttl=60) == 1
    assert c.incr("k", ttl=60) == 2
    c.set("j", "v", ttl=60)
    assert c.get("j") == "v"
    c.set_json("o", {"a": 1})
    assert c.get_json("o") == {"a": 1}

    import app.utils.cache as cache_module

    real_time = cache_module.time.time
    monkeypatch.setattr(cache_module.time, "time", lambda: real_time() + 3600)
    assert c.get("k") is None
    assert c.incr("k", ttl=60) == 1


@pytest.mark.parametrize("raw,expected", [
    ("1,234.5", Decimal("1234.5")), (12, Decimal("12")), (None, None), ("..", None), ("n/a", None),
    (float("nan"), None), (True, None), ("1e20", None), ("-3.25", Decimal("-3.25")),
])
def test_parse_number(raw, expected):
    assert parse_number(raw) == expected


@pytest.mark.parametrize("raw,expected", [("2023", 2023), (2023, 2023), ("2023M01", 2023), ("abcd", None), (None, None), ("1800", None)])
def test_parse_year(raw, expected):
    assert parse_year(raw) == expected


def test_clean_iso2_list():
    assert clean_iso2_list(" et, NG,,ke ,ET") == ["ET", "NG", "KE"]
