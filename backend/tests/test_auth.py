def test_root_and_health_are_public(client):
    assert client.get("/").status_code == 200
    body = client.get("/health").json()
    assert body["status"] == "ok"
    assert body["database"] == "ok"


def test_register_returns_key_once(client):
    resp = client.post("/v1/auth/register", json={"email": "New.User@Example.com", "name": "New"})
    assert resp.status_code == 201
    body = resp.json()
    assert body["api_key"].startswith("afr_live_")
    assert body["tier"] == "free"

    dup = client.post("/v1/auth/register", json={"email": "new.user@example.com"})
    assert dup.status_code == 409


def test_register_rejects_bad_email(client):
    assert client.post("/v1/auth/register", json={"email": "not-an-email"}).status_code == 422


def test_missing_key_is_401(client):
    resp = client.get("/v1/countries")
    assert resp.status_code == 401
    assert "X-API-Key" in resp.json()["detail"]["hint"]


def test_bogus_key_is_401(client):
    assert client.get("/v1/countries", headers={"X-API-Key": "afr_live_nope"}).status_code == 401


def test_me_reports_usage(client, headers):
    client.get("/v1/countries", headers=headers)
    resp = client.get("/v1/auth/me", headers=headers)
    assert resp.status_code == 200
    body = resp.json()
    assert body["email"] == "tester@example.com"
    assert body["tier"] == "free"
    assert body["rate_limit"] == 100
    assert body["requests_this_hour"] >= 2
    assert body["key_prefix"].startswith("afr_live_")


def test_rate_limit_headers_present(client, headers):
    resp = client.get("/v1/countries", headers=headers)
    assert resp.headers["X-RateLimit-Limit"] == "100"
    assert int(resp.headers["X-RateLimit-Remaining"]) < 100
