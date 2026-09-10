def test_compare_specific_year_ranks_desc(client, headers):
    body = client.get("/v1/compare", params={"countries": "et,NG,KE,ZA", "indicator": "GDP_CURRENT_USD", "year": 2023}, headers=headers).json()
    assert body["year"] == 2023
    assert [r["iso2"] for r in body["data"]] == ["NG", "ET", "KE"]
    assert [r["rank"] for r in body["data"]] == [1, 2, 3]
    assert body["missing"] == ["ZA"]
    assert body["countries_reporting"] == 3
    total = 363.8e9 + 163.7e9 + 107.4e9
    assert abs(body["continental_total"] - total) < 1
    assert abs(body["continental_average"] - total / 3) < 1


def test_compare_latest_uses_each_countrys_latest_year(client, headers):
    body = client.get("/v1/compare", params={"countries": "ZA,ET", "indicator": "GDP_CURRENT_USD"}, headers=headers).json()
    by = {r["iso2"]: r for r in body["data"]}
    assert by["ZA"]["year"] == 2022
    assert by["ET"]["year"] == 2023
    assert by["ZA"]["rank"] == 1
    assert body["missing"] == []


def test_compare_mean_indicator_has_no_total(client, headers):
    body = client.get("/v1/compare", params={"countries": "ET,KE", "indicator": "INFLATION_ANNUAL", "year": 2023}, headers=headers).json()
    assert body["continental_total"] is None
    assert abs(body["continental_average"] - (30.2 + 7.7) / 2) < 1e-6


def test_compare_free_tier_limit(client, headers):
    resp = client.get("/v1/compare", params={"countries": "ET,NG,KE,ZA,GH,TZ", "indicator": "GDP_CURRENT_USD"}, headers=headers)
    assert resp.status_code == 400
    assert "Maximum 5" in resp.json()["detail"]


def test_compare_unknown_country_404(client, headers):
    resp = client.get("/v1/compare", params={"countries": "ET,XX", "indicator": "GDP_CURRENT_USD"}, headers=headers)
    assert resp.status_code == 404


def test_compare_trend(client, headers):
    body = client.get("/v1/compare/trend", params={"countries": "ET,KE", "indicator": "GDP_CURRENT_USD", "from": 2021, "to": 2023}, headers=headers).json()
    assert body["from_year"] == 2021 and body["to_year"] == 2023
    series = {s["iso2"]: s["data"] for s in body["series"]}
    assert [p["year"] for p in series["ET"]] == [2021, 2022, 2023]
    assert [p["year"] for p in series["KE"]] == [2021, 2022, 2023]


def test_region_summary(client, headers):
    body = client.get("/v1/regions/east-africa/summary", params={"category": "economy"}, headers=headers).json()
    assert body["region"] == "East Africa"
    assert body["country_count"] == 18
    by = {s["indicator"]["code"]: s for s in body["indicators"]}
    gdp = by["GDP_CURRENT_USD"]
    assert gdp["aggregation"] == "sum"
    assert gdp["countries_reporting"] == 2  # ET + KE
    assert abs(gdp["value"] - (163.7e9 + 107.4e9)) < 1
    assert by["INFLATION_ANNUAL"]["aggregation"] == "mean"


def test_region_unknown_404(client, headers):
    assert client.get("/v1/regions/atlantis/summary", headers=headers).status_code == 404
