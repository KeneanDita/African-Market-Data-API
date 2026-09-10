def test_all_54_countries(client, headers):
    body = client.get("/v1/countries", headers=headers).json()
    assert body["total"] == 54
    assert len({c["iso2"] for c in body["data"]}) == 54
    assert len({c["iso3"] for c in body["data"]}) == 54
    et = next(c for c in body["data"] if c["iso2"] == "ET")
    assert et["name"] == "Ethiopia"
    assert et["currency_code"] == "ETB"
    assert "Amharic" in et["languages"]


def test_region_filter_and_sort(client, headers):
    body = client.get("/v1/countries", params={"region": "east africa", "sort": "area_km2", "order": "desc"}, headers=headers).json()
    assert body["total"] == 18
    assert all(c["region"] == "East Africa" for c in body["data"])
    areas = [c["area_km2"] for c in body["data"]]
    assert areas == sorted(areas, reverse=True)
    assert body["meta"]["region_filter"] == "east africa"


def test_region_counts_sum_to_54(client, headers):
    regions = client.get("/v1/regions", headers=headers).json()
    assert regions["total"] == 5
    assert sum(r["country_count"] for r in regions["data"]) == 54


def test_single_country_case_insensitive(client, headers):
    assert client.get("/v1/countries/ng", headers=headers).json()["name"] == "Nigeria"
    assert client.get("/v1/countries/SC", headers=headers).json()["name"] == "Seychelles"


def test_unknown_country_404(client, headers):
    resp = client.get("/v1/countries/XX", headers=headers)
    assert resp.status_code == 404
    assert "XX" in resp.json()["detail"]


def test_indicators_catalogue(client, headers):
    body = client.get("/v1/indicators", headers=headers).json()
    assert body["total"] == 87
    assert set(body["categories"]) == {"economy", "demographics", "health", "education", "infrastructure", "finance"}
    econ = client.get("/v1/indicators", params={"category": "economy"}, headers=headers).json()
    assert econ["total"] == 25
    gdp = client.get("/v1/indicators/GDP_CURRENT_USD", headers=headers).json()
    assert gdp["source_code"] == "NY.GDP.MKTP.CD"
    assert gdp["aggregation"] == "sum"
