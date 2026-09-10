def gql(client, headers, query: str, variables: dict | None = None):
    resp = client.post("/graphql", json={"query": query, "variables": variables or {}}, headers=headers)
    assert resp.status_code == 200, resp.text
    return resp.json()


def test_graphql_requires_key(client):
    resp = client.post("/graphql", json={"query": "{ countries { iso2 } }"})
    assert resp.status_code == 401


def test_graphiql_page_is_public(client):
    resp = client.get("/graphql", headers={"Accept": "text/html"})
    assert resp.status_code == 200


def test_graphql_countries_and_nested_data(client, headers):
    body = gql(client, headers, """
      query {
        countries(region: "West Africa") { iso2 }
        country(iso2: "ET") {
          name
          dataPoints(indicator: "GDP_CURRENT_USD", from: 2022) { year value indicator { code } }
          latestSnapshot { indicator { code } year value }
        }
      }
    """)
    assert "errors" not in body, body
    data = body["data"]
    assert len(data["countries"]) == 16
    assert data["country"]["name"] == "Ethiopia"
    assert [p["year"] for p in data["country"]["dataPoints"]] == [2022, 2023]
    assert data["country"]["dataPoints"][0]["indicator"]["code"] == "GDP_CURRENT_USD"
    assert {s["indicator"]["code"] for s in data["country"]["latestSnapshot"]} == {"GDP_CURRENT_USD", "POPULATION_TOTAL", "INFLATION_ANNUAL"}


def test_graphql_compare(client, headers):
    body = gql(client, headers, """
      query CompareGDP($countries: [String!]!) {
        compare(countries: $countries, indicator: "GDP_CURRENT_USD", year: 2023) {
          indicator { name unit }
          year
          continentalAverage
          rankings { rank value country { name iso2 } }
          missing
        }
      }
    """, {"countries": ["ET", "KE", "NG", "ZA"]})
    assert "errors" not in body, body
    cmp_ = body["data"]["compare"]
    assert cmp_["year"] == 2023
    assert [r["country"]["iso2"] for r in cmp_["rankings"]] == ["NG", "ET", "KE"]
    assert cmp_["missing"] == ["ZA"]


def test_graphql_errors_are_structured(client, headers):
    body = gql(client, headers, '{ compare(countries: ["ET","XX"], indicator: "GDP_CURRENT_USD") { year } }')
    assert body["errors"][0]["extensions"]["code"] == "NOT_FOUND"
    body = gql(client, headers, '{ country(iso2: "XX") { name } }')
    assert body["data"]["country"] is None


def test_graphql_region_summary(client, headers):
    body = gql(client, headers, '{ regionSummary(region: "East Africa", category: "economy") { indicator { code } value countriesReporting } }')
    assert "errors" not in body, body
    codes = {s["indicator"]["code"] for s in body["data"]["regionSummary"]}
    assert {"GDP_CURRENT_USD", "INFLATION_ANNUAL"} <= codes
