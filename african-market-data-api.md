# 🌍 African Market Data API — Full Build Specification

> **Built by:** Kenean Dita Meleta  
> **Spec target:** Claude Fable 5.1 (upload this file and say "build this project from scratch")  
> **Goal:** A production-grade, free-to-start REST + GraphQL API serving structured economic, demographic, and market data for all 54 African countries — the Bloomberg terminal for the African continent.

---

## 1. Project Overview

### What Is This?

A public data API platform that aggregates, cleans, normalizes, and serves African economic and market data through a developer-friendly interface. Think of it as a single source of truth for African data — something that **does not properly exist today**.

### Why It Matters

- African economic data is scattered across World Bank, IMF, UN, African Development Bank, and dozens of national statistics bureaus
- It's inconsistent in format, often outdated when accessed manually, and almost never queryable via API
- Developers, researchers, journalists, and fintech startups building African products have **no clean API to call**
- This fills that gap — for free at its core, with a paid tier for power users

### Who Uses It?

| User | Use Case |
|---|---|
| Fintech startups | FX rates, GDP, inflation for pricing models |
| Journalists | Real-time economic comparison across countries |
| Researchers | Historical demographic and economic time series |
| NGOs | Poverty, education, health indicators |
| Developers | Build dashboards, apps, tools on African data |

---

## 2. Tech Stack (100% Free to Start)

### Backend
| Layer | Technology | Why |
|---|---|---|
| Language | **Python 3.11+** | Best for data engineering + APIs |
| API Framework | **FastAPI** | Auto docs, async, fast, modern |
| GraphQL | **Strawberry** (Python GraphQL lib) | Pythonic, works with FastAPI |
| Database | **PostgreSQL 15** | Relational, time-series friendly |
| Cache | **Redis** | Rate limiting + response caching |
| Task Queue | **Celery + Redis** | Background data scraping jobs |
| ORM | **SQLAlchemy 2.0 + Alembic** | Schema migrations |
| Scraping | **httpx + BeautifulSoup4 + Playwright** | Async HTTP + JS-rendered pages |

### Frontend (Dashboard + Docs)
| Layer | Technology |
|---|---|
| Framework | **Next.js 14 (App Router)** |
| Styling | **Tailwind CSS** |
| Charts | **Recharts + D3.js** |
| API Docs | **Auto-generated from FastAPI (Swagger + ReDoc)** |
| Auth UI | **NextAuth.js** |

### Infrastructure (Free Tier)
| Service | Provider | Free Limit |
|---|---|---|
| Hosting (API) | **Railway** or **Render** | 500 hrs/month free |
| Database | **Supabase** | 500MB free PostgreSQL |
| Cache | **Upstash Redis** | 10,000 req/day free |
| Frontend | **Vercel** | Unlimited for hobby |
| CI/CD | **GitHub Actions** | 2,000 min/month free |

---

## 3. Data Sources (All Free & Open)

```
These are the upstream sources the scrapers will pull from.
All are publicly available with no API key required.
```

| Source | Data Provided | URL |
|---|---|---|
| World Bank Open Data | GDP, inflation, trade, debt, population | data.worldbank.org/api |
| African Development Bank | Infrastructure, finance, development | dataportal.afdb.org |
| UN Data | Demographics, education, health | data.un.org |
| IMF Data API | Fiscal, monetary, balance of payments | imf.org/external/datamapper |
| UNCTAD | Trade statistics, FDI | unctadstat.unctad.org |
| WHO Data | Health indicators | apps.who.int/gho/data |
| National Stats Bureaus | Country-specific granular data | (per country, scraped) |

**Key insight:** The World Bank and IMF both have free public APIs. Most data can be pulled directly via HTTP — no scraping needed for the core dataset.

---

## 4. Database Schema

### Core Tables

```sql
-- All 54 African countries
CREATE TABLE countries (
  id           SERIAL PRIMARY KEY,
  iso2         CHAR(2) UNIQUE NOT NULL,        -- e.g. "ET"
  iso3         CHAR(3) UNIQUE NOT NULL,        -- e.g. "ETH"
  name         VARCHAR(100) NOT NULL,          -- e.g. "Ethiopia"
  region       VARCHAR(50),                    -- e.g. "East Africa"
  capital      VARCHAR(100),
  currency     VARCHAR(10),
  currency_code CHAR(3),
  population   BIGINT,
  area_km2     BIGINT,
  languages    TEXT[],
  created_at   TIMESTAMPTZ DEFAULT NOW()
);

-- Indicator definitions (GDP, inflation, etc.)
CREATE TABLE indicators (
  id           SERIAL PRIMARY KEY,
  code         VARCHAR(50) UNIQUE NOT NULL,    -- e.g. "GDP_CURRENT_USD"
  name         VARCHAR(200) NOT NULL,          -- e.g. "GDP (current US$)"
  category     VARCHAR(50) NOT NULL,           -- e.g. "economy", "demographics"
  subcategory  VARCHAR(50),
  unit         VARCHAR(50),                    -- e.g. "USD", "percent", "per_capita"
  description  TEXT,
  source       VARCHAR(100),                   -- e.g. "World Bank"
  source_code  VARCHAR(100),                   -- original code in source system
  created_at   TIMESTAMPTZ DEFAULT NOW()
);

-- Time-series data points
CREATE TABLE data_points (
  id           BIGSERIAL PRIMARY KEY,
  country_id   INT REFERENCES countries(id),
  indicator_id INT REFERENCES indicators(id),
  year         SMALLINT NOT NULL,
  value        NUMERIC(20, 6),
  source       VARCHAR(100),
  scraped_at   TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(country_id, indicator_id, year)
);

-- API users
CREATE TABLE api_users (
  id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email        VARCHAR(255) UNIQUE NOT NULL,
  name         VARCHAR(200),
  api_key      VARCHAR(64) UNIQUE NOT NULL,
  tier         VARCHAR(20) DEFAULT 'free',     -- free | pro | enterprise
  rate_limit   INT DEFAULT 100,               -- req/hour
  created_at   TIMESTAMPTZ DEFAULT NOW(),
  last_seen_at TIMESTAMPTZ
);

-- Request logs (for rate limiting + analytics)
CREATE TABLE request_logs (
  id           BIGSERIAL PRIMARY KEY,
  api_key      VARCHAR(64),
  endpoint     VARCHAR(200),
  method       VARCHAR(10),
  status_code  SMALLINT,
  response_ms  INT,
  ip_address   INET,
  created_at   TIMESTAMPTZ DEFAULT NOW()
);
```

### Indexes

```sql
-- Most critical for performance
CREATE INDEX idx_data_points_country_indicator ON data_points(country_id, indicator_id);
CREATE INDEX idx_data_points_year ON data_points(year);
CREATE INDEX idx_request_logs_api_key_created ON request_logs(api_key, created_at);
CREATE INDEX idx_countries_iso2 ON countries(iso2);
CREATE INDEX idx_countries_region ON countries(region);
```

---

## 5. Project Folder Structure

```
african-market-api/
│
├── backend/
│   ├── app/
│   │   ├── main.py                    # FastAPI app entry point
│   │   ├── config.py                  # Settings (env vars)
│   │   ├── database.py                # SQLAlchemy engine + session
│   │   │
│   │   ├── models/                    # SQLAlchemy ORM models
│   │   │   ├── __init__.py
│   │   │   ├── country.py
│   │   │   ├── indicator.py
│   │   │   ├── data_point.py
│   │   │   └── api_user.py
│   │   │
│   │   ├── schemas/                   # Pydantic response schemas
│   │   │   ├── __init__.py
│   │   │   ├── country.py
│   │   │   ├── indicator.py
│   │   │   └── data_point.py
│   │   │
│   │   ├── routers/                   # REST API route handlers
│   │   │   ├── __init__.py
│   │   │   ├── countries.py
│   │   │   ├── indicators.py
│   │   │   ├── data.py
│   │   │   ├── compare.py
│   │   │   └── auth.py
│   │   │
│   │   ├── graphql/                   # Strawberry GraphQL schema
│   │   │   ├── __init__.py
│   │   │   ├── schema.py
│   │   │   ├── types.py
│   │   │   └── resolvers.py
│   │   │
│   │   ├── scrapers/                  # Data ingestion workers
│   │   │   ├── __init__.py
│   │   │   ├── base.py                # Abstract base scraper
│   │   │   ├── world_bank.py
│   │   │   ├── imf.py
│   │   │   ├── un_data.py
│   │   │   ├── afdb.py
│   │   │   └── scheduler.py          # Celery task scheduling
│   │   │
│   │   ├── middleware/
│   │   │   ├── rate_limiter.py        # Redis-backed rate limiting
│   │   │   ├── api_key_auth.py        # API key validation
│   │   │   └── request_logger.py      # Log all requests
│   │   │
│   │   └── utils/
│   │       ├── cache.py               # Redis cache helpers
│   │       ├── countries_seed.py      # Seed all 54 countries
│   │       └── normalizer.py          # Data normalization utils
│   │
│   ├── alembic/                       # DB migrations
│   ├── tests/
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env.example
│
├── frontend/
│   ├── app/
│   │   ├── page.tsx                   # Landing page
│   │   ├── docs/page.tsx              # Documentation
│   │   ├── dashboard/page.tsx         # User dashboard
│   │   ├── explorer/page.tsx          # Data explorer
│   │   └── layout.tsx
│   │
│   ├── components/
│   │   ├── CountryCard.tsx
│   │   ├── DataChart.tsx
│   │   ├── CompareTable.tsx
│   │   ├── ApiKeyWidget.tsx
│   │   └── EndpointExample.tsx
│   │
│   ├── lib/
│   │   └── api.ts                     # API client helpers
│   │
│   └── package.json
│
├── docker-compose.yml                  # Local dev: postgres + redis + api
└── README.md
```

---

## 6. REST API Endpoints

### Base URL
```
https://api.africadata.dev/v1
```

### Authentication
All endpoints require an API key in the header:
```
X-API-Key: your_api_key_here
```

---

### 6.1 Countries

#### `GET /countries`
Returns all 54 African countries with metadata.

**Response:**
```json
{
  "data": [
    {
      "iso2": "ET",
      "iso3": "ETH",
      "name": "Ethiopia",
      "region": "East Africa",
      "capital": "Addis Ababa",
      "currency": "Ethiopian Birr",
      "currency_code": "ETB",
      "population": 126527060,
      "area_km2": 1104300,
      "languages": ["Amharic", "Oromo", "Tigrinya"]
    }
  ],
  "total": 54,
  "meta": {
    "region_filter": null
  }
}
```

**Query params:**
- `?region=East Africa` — filter by region
- `?sort=population&order=desc`

---

#### `GET /countries/{iso2}`
Returns a single country's full profile.

**Example:** `GET /countries/ET`

---

### 6.2 Indicators

#### `GET /indicators`
Returns all available data indicators.

**Response:**
```json
{
  "data": [
    {
      "code": "GDP_CURRENT_USD",
      "name": "GDP (current US$)",
      "category": "economy",
      "subcategory": "output",
      "unit": "USD",
      "source": "World Bank",
      "description": "Gross domestic product at purchaser's prices..."
    }
  ],
  "total": 87
}
```

**Query params:**
- `?category=economy`
- `?category=demographics`
- `?category=health`
- `?category=education`
- `?category=trade`

---

### 6.3 Data (Core Endpoint)

#### `GET /data/{iso2}/{indicator_code}`
Returns the full time series for one country + one indicator.

**Example:** `GET /data/ET/GDP_CURRENT_USD`

**Response:**
```json
{
  "country": {
    "iso2": "ET",
    "name": "Ethiopia"
  },
  "indicator": {
    "code": "GDP_CURRENT_USD",
    "name": "GDP (current US$)",
    "unit": "USD"
  },
  "data": [
    { "year": 2000, "value": 8189700000 },
    { "year": 2001, "value": 7909500000 },
    { "year": 2005, "value": 12385600000 },
    { "year": 2010, "value": 29934800000 },
    { "year": 2015, "value": 64604700000 },
    { "year": 2020, "value": 107646800000 },
    { "year": 2023, "value": 155801400000 }
  ],
  "latest": { "year": 2023, "value": 155801400000 },
  "source": "World Bank",
  "last_updated": "2024-11-01T00:00:00Z"
}
```

**Query params:**
- `?from=2010&to=2023` — year range filter
- `?latest=true` — return only the most recent value

---

#### `GET /data/{iso2}`
Returns ALL latest indicator values for a country (country snapshot).

**Example:** `GET /data/NG` → full snapshot of Nigeria

---

### 6.4 Compare (Most Powerful Endpoint)

#### `GET /compare`
Compare one or more indicators across multiple countries.

**Query params:**
- `countries=ET,NG,KE,ZA,GH` (comma-separated iso2 codes)
- `indicator=GDP_CURRENT_USD`
- `year=2023` (optional, defaults to latest)

**Example:**
```
GET /compare?countries=ET,NG,KE,ZA&indicator=GDP_CURRENT_USD&year=2023
```

**Response:**
```json
{
  "indicator": {
    "code": "GDP_CURRENT_USD",
    "name": "GDP (current US$)",
    "unit": "USD"
  },
  "year": 2023,
  "data": [
    { "iso2": "ZA", "name": "South Africa",  "value": 377782000000, "rank": 1 },
    { "iso2": "NG", "name": "Nigeria",        "value": 362812000000, "rank": 2 },
    { "iso2": "ET", "name": "Ethiopia",       "value": 155801400000, "rank": 3 },
    { "iso2": "KE", "name": "Kenya",          "value": 107441800000, "rank": 4 }
  ],
  "continental_average": 66241200000,
  "continental_total": 3575824800000
}
```

---

#### `GET /compare/trend`
Compare time-series trends of one indicator across multiple countries.

**Example:**
```
GET /compare/trend?countries=ET,KE,GH&indicator=GDP_GROWTH_ANNUAL&from=2010&to=2023
```

---

### 6.5 Regions

#### `GET /regions`
Returns Africa's sub-regions with member countries.

**Regions:** North Africa, West Africa, East Africa, Central Africa, Southern Africa

#### `GET /regions/{region}/summary`
Returns aggregated indicators for all countries in a region.

---

### 6.6 Auth

#### `POST /auth/register`
Register for a free API key.

**Body:**
```json
{
  "email": "dev@example.com",
  "name": "Abebe Girma"
}
```

**Response:**
```json
{
  "api_key": "afr_live_xxxxxxxxxxxxxxxxxxxx",
  "tier": "free",
  "rate_limit": "100 requests/hour",
  "docs": "https://africadata.dev/docs"
}
```

---

## 7. GraphQL API

**Endpoint:** `POST /graphql`

### Schema

```graphql
type Country {
  iso2: String!
  iso3: String!
  name: String!
  region: String
  capital: String
  currency: String
  population: Int
  dataPoints(indicator: String, from: Int, to: Int): [DataPoint]
  latestSnapshot: [IndicatorSnapshot]
}

type Indicator {
  code: String!
  name: String!
  category: String!
  unit: String
  description: String
}

type DataPoint {
  year: Int!
  value: Float
  indicator: Indicator
}

type IndicatorSnapshot {
  indicator: Indicator!
  value: Float
  year: Int
}

type CompareResult {
  indicator: Indicator!
  year: Int!
  rankings: [CountryRanking!]!
  continentalAverage: Float
}

type CountryRanking {
  country: Country!
  value: Float
  rank: Int!
}

type Query {
  countries(region: String): [Country!]!
  country(iso2: String!): Country
  indicators(category: String): [Indicator!]!
  indicator(code: String!): Indicator
  data(iso2: String!, indicator: String!, from: Int, to: Int): [DataPoint!]!
  compare(countries: [String!]!, indicator: String!, year: Int): CompareResult!
  regionSummary(region: String!): [IndicatorSnapshot!]!
}
```

### Example Query

```graphql
query CompareGDP {
  compare(
    countries: ["ET", "KE", "GH", "NG"]
    indicator: "GDP_CURRENT_USD"
    year: 2023
  ) {
    indicator { name, unit }
    year
    continentalAverage
    rankings {
      rank
      value
      country { name, iso2 }
    }
  }
}
```

---

## 8. Core Backend Code

### `backend/app/main.py`

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import strawberry
from strawberry.fastapi import GraphQLRouter

from app.routers import countries, indicators, data, compare, auth
from app.graphql.schema import schema
from app.middleware.rate_limiter import RateLimiterMiddleware
from app.middleware.request_logger import RequestLoggerMiddleware
from app.database import engine, Base

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="African Market Data API",
    description="The single source of truth for African economic & demographic data.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# Custom middleware
app.add_middleware(RateLimiterMiddleware)
app.add_middleware(RequestLoggerMiddleware)

# REST routes
app.include_router(auth.router,        prefix="/v1/auth",       tags=["Auth"])
app.include_router(countries.router,   prefix="/v1/countries",  tags=["Countries"])
app.include_router(indicators.router,  prefix="/v1/indicators", tags=["Indicators"])
app.include_router(data.router,        prefix="/v1/data",       tags=["Data"])
app.include_router(compare.router,     prefix="/v1/compare",    tags=["Compare"])

# GraphQL
graphql_app = GraphQLRouter(schema)
app.include_router(graphql_app, prefix="/graphql")

@app.get("/")
def root():
    return {
        "name": "African Market Data API",
        "version": "1.0.0",
        "docs": "/docs",
        "graphql": "/graphql",
        "status": "operational"
    }

@app.get("/health")
def health():
    return { "status": "ok" }
```

---

### `backend/app/scrapers/world_bank.py`

```python
import httpx
import asyncio
from typing import Optional
from app.database import SessionLocal
from app.models.data_point import DataPoint
from app.models.country import Country
from app.models.indicator import Indicator

WORLD_BANK_BASE = "https://api.worldbank.org/v2"

# Maps our internal indicator codes → World Bank indicator codes
INDICATOR_MAP = {
    "GDP_CURRENT_USD":        "NY.GDP.MKTP.CD",
    "GDP_GROWTH_ANNUAL":      "NY.GDP.MKTP.KD.ZG",
    "GDP_PER_CAPITA_USD":     "NY.GDP.PCAP.CD",
    "INFLATION_ANNUAL":       "FP.CPI.TOTL.ZG",
    "UNEMPLOYMENT_RATE":      "SL.UEM.TOTL.ZS",
    "POPULATION_TOTAL":       "SP.POP.TOTL",
    "POPULATION_GROWTH":      "SP.POP.GROW",
    "LIFE_EXPECTANCY":        "SP.DYN.LE00.IN",
    "LITERACY_RATE":          "SE.ADT.LITR.ZS",
    "TRADE_GDP_PERCENT":      "NE.TRD.GNFS.ZS",
    "EXPORTS_CURRENT_USD":    "NE.EXP.GNFS.CD",
    "IMPORTS_CURRENT_USD":    "NE.IMP.GNFS.CD",
    "FOREIGN_INVESTMENT_NET": "BX.KLT.DINV.CD.WD",
    "POVERTY_RATE":           "SI.POV.NAHC",
    "GINI_INDEX":             "SI.POV.GINI",
    "INTERNET_USERS_PCT":     "IT.NET.USER.ZS",
    "MOBILE_SUBSCRIPTIONS":   "IT.CEL.SETS.P2",
    "CO2_EMISSIONS_PER_CAP":  "EN.ATM.CO2E.PC",
    "ACCESS_TO_ELECTRICITY":  "EG.ELC.ACCS.ZS",
}

AFRICAN_ISO2_CODES = [
    "DZ","AO","BJ","BW","BF","BI","CV","CM","CF","TD","KM","CG","CD",
    "DJ","EG","GQ","ER","SZ","ET","GA","GM","GH","GN","GW","CI","KE",
    "LS","LR","LY","MG","MW","ML","MR","MU","MA","MZ","NA","NE","NG",
    "RW","ST","SN","SL","SO","ZA","SS","SD","TZ","TG","TN","UG","ZM","ZW"
]

async def fetch_country_indicator(
    client: httpx.AsyncClient,
    iso2: str,
    wb_indicator: str,
    from_year: int = 2000,
    to_year: int = 2024
) -> list[dict]:
    """Fetch time series data from World Bank API for one country + indicator."""
    url = f"{WORLD_BANK_BASE}/country/{iso2}/indicator/{wb_indicator}"
    params = {
        "format": "json",
        "per_page": 100,
        "mrv": to_year - from_year + 1,
        "date": f"{from_year}:{to_year}"
    }
    try:
        resp = await client.get(url, params=params, timeout=30.0)
        resp.raise_for_status()
        json_data = resp.json()
        if len(json_data) < 2 or not json_data[1]:
            return []
        return [
            {"year": int(item["date"]), "value": item["value"]}
            for item in json_data[1]
            if item["value"] is not None
        ]
    except Exception as e:
        print(f"[WorldBank] Error fetching {iso2}/{wb_indicator}: {e}")
        return []


async def scrape_all():
    """Main scraper: pulls all indicators for all African countries."""
    db = SessionLocal()
    async with httpx.AsyncClient() as client:
        for our_code, wb_code in INDICATOR_MAP.items():
            indicator = db.query(Indicator).filter_by(code=our_code).first()
            if not indicator:
                print(f"[WorldBank] Indicator {our_code} not found in DB, skipping")
                continue

            for iso2 in AFRICAN_ISO2_CODES:
                country = db.query(Country).filter_by(iso2=iso2).first()
                if not country:
                    continue

                data_rows = await fetch_country_indicator(client, iso2, wb_code)
                for row in data_rows:
                    existing = db.query(DataPoint).filter_by(
                        country_id=country.id,
                        indicator_id=indicator.id,
                        year=row["year"]
                    ).first()
                    if existing:
                        existing.value = row["value"]
                    else:
                        db.add(DataPoint(
                            country_id=country.id,
                            indicator_id=indicator.id,
                            year=row["year"],
                            value=row["value"],
                            source="World Bank"
                        ))

                db.commit()
                print(f"[WorldBank] ✓ {iso2} / {our_code} — {len(data_rows)} points")
                await asyncio.sleep(0.2)  # Be polite to the API

    db.close()
    print("[WorldBank] Scrape complete.")
```

---

### `backend/app/middleware/rate_limiter.py`

```python
import time
import redis
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware

# Tiers: requests per hour
TIER_LIMITS = {
    "free":       100,
    "pro":        5000,
    "enterprise": 100000,
}

class RateLimiterMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, redis_url: str = "redis://localhost:6379"):
        super().__init__(app)
        self.redis = redis.from_url(redis_url, decode_responses=True)

    async def dispatch(self, request: Request, call_next):
        # Skip rate limit for docs and health
        if request.url.path in ["/docs", "/redoc", "/health", "/", "/openapi.json"]:
            return await call_next(request)

        api_key = request.headers.get("X-API-Key")
        if not api_key:
            raise HTTPException(status_code=401, detail="API key required. Get one free at africadata.dev")

        # Look up tier from cache or DB
        tier = self.redis.get(f"tier:{api_key}") or "free"
        limit = TIER_LIMITS.get(tier, 100)

        # Sliding window: bucket per hour
        window = int(time.time() // 3600)
        key = f"ratelimit:{api_key}:{window}"

        current = self.redis.incr(key)
        if current == 1:
            self.redis.expire(key, 3600)

        if current > limit:
            raise HTTPException(
                status_code=429,
                detail={
                    "error": "Rate limit exceeded",
                    "limit": limit,
                    "tier": tier,
                    "reset_in": f"{3600 - (int(time.time()) % 3600)} seconds",
                    "upgrade": "https://africadata.dev/pricing"
                }
            )

        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(limit)
        response.headers["X-RateLimit-Remaining"] = str(max(0, limit - current))
        return response
```

---

### `backend/app/routers/compare.py`

```python
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.country import Country
from app.models.indicator import Indicator
from app.models.data_point import DataPoint

router = APIRouter()

@router.get("")
def compare_countries(
    countries: str = Query(..., description="Comma-separated ISO2 codes, e.g. ET,NG,KE"),
    indicator: str = Query(..., description="Indicator code, e.g. GDP_CURRENT_USD"),
    year: int = Query(None, description="Year (defaults to latest available)"),
    db: Session = Depends(get_db)
):
    iso2_list = [c.strip().upper() for c in countries.split(",")]
    if len(iso2_list) > 10:
        raise HTTPException(status_code=400, detail="Maximum 10 countries per comparison")

    ind = db.query(Indicator).filter_by(code=indicator).first()
    if not ind:
        raise HTTPException(status_code=404, detail=f"Indicator '{indicator}' not found")

    results = []
    all_values = []

    for iso2 in iso2_list:
        country = db.query(Country).filter_by(iso2=iso2).first()
        if not country:
            continue

        query = db.query(DataPoint).filter_by(country_id=country.id, indicator_id=ind.id)
        if year:
            dp = query.filter_by(year=year).first()
        else:
            dp = query.order_by(DataPoint.year.desc()).first()

        if dp:
            results.append({
                "iso2": country.iso2,
                "name": country.name,
                "year": dp.year,
                "value": float(dp.value) if dp.value else None
            })
            if dp.value:
                all_values.append(float(dp.value))

    # Rank by value descending
    results.sort(key=lambda x: (x["value"] or 0), reverse=True)
    for i, r in enumerate(results):
        r["rank"] = i + 1

    continental_average = sum(all_values) / len(all_values) if all_values else None

    return {
        "indicator": {
            "code": ind.code,
            "name": ind.name,
            "unit": ind.unit
        },
        "data": results,
        "continental_average": continental_average
    }
```

---

## 9. Frontend: Data Explorer Page

The frontend has a **Data Explorer** — a beautiful interactive page where users can:

1. Pick a country from a map or dropdown
2. Pick an indicator category (Economy, Demographics, Health, Trade...)
3. See a time-series chart rendered with Recharts
4. Switch to "Compare mode" to overlay multiple countries
5. Export data as CSV or JSON

### Key Pages

| Route | Purpose |
|---|---|
| `/` | Landing page with hero stats (Africa's total GDP, fastest growing economies) |
| `/docs` | Full API documentation with live examples |
| `/explorer` | Interactive data explorer (the killer feature) |
| `/dashboard` | User dashboard with API key, usage stats |
| `/graphql` | GraphQL playground |
| `/pricing` | Free vs Pro tier comparison |

---

## 10. Indicators to Seed (87 Total)

### Economy (25)
`GDP_CURRENT_USD`, `GDP_PPP_USD`, `GDP_GROWTH_ANNUAL`, `GDP_PER_CAPITA_USD`,
`GDP_PER_CAPITA_PPP`, `GNI_CURRENT_USD`, `GNI_PER_CAPITA_ATLAS`,
`INFLATION_ANNUAL`, `INFLATION_CONSUMER_PRICES`, `UNEMPLOYMENT_RATE`,
`YOUTH_UNEMPLOYMENT`, `GOVERNMENT_DEBT_GDP`, `FISCAL_BALANCE_GDP`,
`CURRENT_ACCOUNT_BALANCE_GDP`, `FOREIGN_RESERVES_USD`,
`FOREIGN_INVESTMENT_NET`, `FOREIGN_INVESTMENT_INFLOWS`,
`REMITTANCES_INFLOWS_USD`, `REMITTANCES_GDP_PCT`,
`EXPORTS_CURRENT_USD`, `IMPORTS_CURRENT_USD`, `TRADE_BALANCE_USD`,
`TRADE_GDP_PERCENT`, `GINI_INDEX`, `POVERTY_RATE`

### Demographics (18)
`POPULATION_TOTAL`, `POPULATION_GROWTH`, `POPULATION_DENSITY`,
`URBAN_POPULATION`, `URBAN_POPULATION_PCT`, `RURAL_POPULATION`,
`MEDIAN_AGE`, `BIRTH_RATE`, `DEATH_RATE`, `FERTILITY_RATE`,
`INFANT_MORTALITY`, `UNDER5_MORTALITY`, `LIFE_EXPECTANCY`,
`LIFE_EXPECTANCY_MALE`, `LIFE_EXPECTANCY_FEMALE`,
`NET_MIGRATION`, `DEPENDENCY_RATIO`, `YOUTH_POPULATION_PCT`

### Health (15)
`HEALTH_EXPENDITURE_GDP`, `HEALTH_EXPENDITURE_PER_CAPITA`,
`PHYSICIANS_PER_1000`, `HOSPITAL_BEDS_PER_1000`,
`IMMUNIZATION_DTP`, `IMMUNIZATION_MEASLES`,
`HIV_PREVALENCE`, `MALARIA_INCIDENCE`, `TUBERCULOSIS_INCIDENCE`,
`MATERNAL_MORTALITY`, `ACCESS_TO_SANITATION`, `ACCESS_TO_WATER`,
`STUNTING_CHILDREN`, `WASTING_CHILDREN`, `OBESITY_ADULT`

### Education (12)
`LITERACY_RATE`, `LITERACY_RATE_MALE`, `LITERACY_RATE_FEMALE`,
`SCHOOL_ENROLLMENT_PRIMARY`, `SCHOOL_ENROLLMENT_SECONDARY`,
`SCHOOL_ENROLLMENT_TERTIARY`, `EDUCATION_EXPENDITURE_GDP`,
`PUPIL_TEACHER_RATIO_PRIMARY`, `TRAINED_TEACHERS_PCT`,
`COMPLETION_RATE_PRIMARY`, `COMPLETION_RATE_SECONDARY`,
`OUT_OF_SCHOOL_CHILDREN`

### Infrastructure & Tech (10)
`ACCESS_TO_ELECTRICITY`, `RENEWABLE_ENERGY_PCT`,
`INTERNET_USERS_PCT`, `MOBILE_SUBSCRIPTIONS`,
`BROADBAND_SUBSCRIPTIONS`, `SECURE_INTERNET_SERVERS`,
`ROAD_DENSITY`, `RAIL_LINES_KM`, `AIR_TRANSPORT_PASSENGERS`,
`CO2_EMISSIONS_PER_CAP`

### Finance (7)
`BANK_ACCOUNTS_PCT`, `MOBILE_MONEY_ACCOUNTS_PCT`,
`DOMESTIC_CREDIT_GDP`, `STOCK_MARKET_CAPITALIZATION_GDP`,
`MICROFINANCE_BORROWERS`, `INSURANCE_PENETRATION`,
`INTEREST_RATE_LENDING`

---

## 11. Rate Limits & Tiers

| Feature | Free | Pro ($29/mo) | Enterprise (Custom) |
|---|---|---|---|
| Requests/hour | 100 | 5,000 | Unlimited |
| Historical data | 2000–present | 1960–present | 1960–present |
| Indicators | All 87 | All 87 + forecasts | All + custom feeds |
| Compare countries | Up to 5 | Up to 54 | Up to 54 |
| GraphQL | ✅ | ✅ | ✅ |
| CSV export | ❌ | ✅ | ✅ |
| Webhooks | ❌ | ✅ | ✅ |
| SLA | None | 99.9% | 99.99% |
| Support | Community | Email | Dedicated |

---

## 12. Build Order (Phase by Phase)

### Phase 1 — Core API (Week 1–2)
```
✅ Set up FastAPI project structure
✅ PostgreSQL schema + Alembic migrations
✅ Seed 54 countries
✅ Seed 87 indicators
✅ World Bank scraper (covers ~70% of indicators)
✅ Basic REST endpoints: /countries, /indicators, /data
✅ Redis rate limiting middleware
✅ API key auth
✅ Deploy to Railway + Supabase
```

### Phase 2 — Power Features (Week 3–4)
```
✅ /compare endpoint (the killer feature)
✅ /compare/trend endpoint
✅ /regions endpoints
✅ GraphQL API with Strawberry
✅ IMF + UN data scrapers
✅ Celery scheduler (auto re-scrape weekly)
✅ Response caching (Redis, 1hr TTL)
✅ Request logging
```

### Phase 3 — Frontend (Week 5–6)
```
✅ Next.js landing page with live hero stats
✅ Interactive data explorer
✅ API documentation page
✅ User registration + dashboard
✅ Usage analytics widget
✅ Mobile responsive
```

### Phase 4 — Polish & Launch (Week 7–8)
```
✅ README + full docs
✅ Postman collection
✅ SDKs: Python + JavaScript client libraries
✅ Blog post: "I built the Bloomberg terminal for Africa"
✅ Submit to Product Hunt
✅ Publish on GitHub
```

---

## 13. Environment Variables

```bash
# .env.example

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/africadata

# Redis
REDIS_URL=redis://localhost:6379

# App
SECRET_KEY=your-secret-key-here
ENVIRONMENT=development
API_BASE_URL=http://localhost:8000

# Email (for API key delivery)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your@gmail.com
SMTP_PASS=your-app-password

# Frontend
NEXT_PUBLIC_API_URL=http://localhost:8000/v1
```

---

## 14. Docker Compose (Local Dev)

```yaml
version: "3.9"

services:
  db:
    image: postgres:15
    environment:
      POSTGRES_DB: africadata
      POSTGRES_USER: kenean
      POSTGRES_PASSWORD: devpassword
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  api:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql://kenean:devpassword@db:5432/africadata
      REDIS_URL: redis://redis:6379
    depends_on:
      - db
      - redis
    volumes:
      - ./backend:/app
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

  worker:
    build: ./backend
    environment:
      DATABASE_URL: postgresql://kenean:devpassword@db:5432/africadata
      REDIS_URL: redis://redis:6379
    depends_on:
      - db
      - redis
    command: celery -A app.scrapers.scheduler worker --loglevel=info

volumes:
  postgres_data:
```

---

## 15. What Makes This Portfolio-Defining

When you show this project, you are demonstrating:

| Skill | Evidence |
|---|---|
| **Data Engineering** | Multi-source scraping pipeline, normalization, time-series storage |
| **API Design** | REST + GraphQL, versioning, pagination, filtering |
| **Systems Design** | Rate limiting, caching, background jobs, middleware |
| **Backend Engineering** | FastAPI, SQLAlchemy, Celery, Redis |
| **Database Design** | Normalized schema, proper indexing, migrations |
| **Frontend Engineering** | Next.js, data visualization, responsive design |
| **DevOps** | Docker Compose, CI/CD, cloud deployment |
| **Product Thinking** | Tiered pricing, real market gap, clear user personas |

This is not a tutorial project. This is something you can point a potential employer or client to and say: **"I identified a gap in the African tech ecosystem, built the infrastructure to fill it, and deployed it."**

---

*Built by Kenean Dita Meleta — keneandita.me*
