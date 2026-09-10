def test_series_full(client, headers):
    body = client.get("/v1/data/ET/GDP_CURRENT_USD", headers=headers).json()
    assert body["country"]["iso2"] == "ET"
    assert body["indicator"]["code"] == "GDP_CURRENT_USD"
    years = [p["year"] for p in body["data"]]
    # free tier: 1995 is hidden (pre-2000)
    assert years == [2019, 2020, 2021, 2022, 2023]
    assert body["latest"] == {"year": 2023, "value": 163.7e9}
    assert body["source"] == "World Bank"
    assert body["last_updated"] is not None


def test_series_year_range_and_latest(client, headers):
    body = client.get("/v1/data/ET/GDP_CURRENT_USD", params={"from": 2020, "to": 2021}, headers=headers).json()
    assert [p["year"] for p in body["data"]] == [2020, 2021]

    body = client.get("/v1/data/ET/GDP_CURRENT_USD", params={"latest": "true"}, headers=headers).json()
    assert body["count"] == 1
    assert body["data"][0]["year"] == 2023


def test_series_empty_for_indicator_without_data(client, headers):
    body = client.get("/v1/data/ET/GINI_INDEX", headers=headers).json()
    assert body["data"] == []
    assert body["latest"] is None
    assert body["count"] == 0


def test_series_unknown_indicator_404(client, headers):
    assert client.get("/v1/data/ET/NOT_A_THING", headers=headers).status_code == 404


def test_snapshot(client, headers):
    body = client.get("/v1/data/ET", headers=headers).json()
    codes = {row["indicator"]["code"]: row for row in body["data"]}
    assert body["total"] == 3
    assert codes["GDP_CURRENT_USD"]["year"] == 2023
    assert codes["POPULATION_TOTAL"]["value"] == 126_527_060
    assert codes["INFLATION_ANNUAL"]["category"] == "economy"

    econ = client.get("/v1/data/ET", params={"category": "economy"}, headers=headers).json()
    assert {r["indicator"]["code"] for r in econ["data"]} == {"GDP_CURRENT_USD", "INFLATION_ANNUAL"}


def test_response_cache_hit(client, headers):
    first = client.get("/v1/data/KE/GDP_CURRENT_USD", headers=headers)
    second = client.get("/v1/data/KE/GDP_CURRENT_USD", headers=headers)
    assert first.headers["X-Cache"] == "MISS"
    assert second.headers["X-Cache"] == "HIT"
    assert first.json() == second.json()
