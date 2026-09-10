# African Market Data API

> The single source of truth for African economic, demographic and market data — **54 countries, 87 indicators, time series back to 1960**, served over REST and GraphQL.

Built by [Kenean Dita Meleta](https://keneandita.me). Full product spec: [african-market-data-api.md](african-market-data-api.md).

```
GET /v1/compare?countries=ET,NG,KE,ZA,EG&indicator=GDP_CURRENT_USD&year=2023

1. Nigeria        $487.4B
2. Egypt          $395.9B
3. South Africa   $381.4B
4. Ethiopia       $135.9B
5. Kenya          $107.5B
continental total: $2.99T · average: $57.6B · 52 countries reporting
```

## What's inside

| | |
|---|---|
| `backend/` | FastAPI + Strawberry GraphQL, SQLAlchemy 2 + Alembic, Redis-backed rate limiting & response cache, Celery scrapers for World Bank / IMF / WHO / UN |
| `frontend/` | Next.js 14 (App Router) + Tailwind + Recharts: landing, docs, interactive data explorer, API-key dashboard, pricing |
| `docker-compose.yml` | Postgres 15 + Redis 7 + API + Celery worker/beat + frontend, one command |
| `.github/workflows/ci.yml` | pytest + Alembic smoke test, `next lint` + `next build` |

## Quick start (zero config)

The backend defaults to SQLite and an in-memory cache, so you can run it with nothing but Python.

```bash
cd backend
python -m venv .venv && .venv\Scripts\activate      # macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt

python -m app.cli seed                               # 54 countries + 87 indicators
python -m app.cli scrape --source world_bank         # ~80 indicators, all years (~2 min)
python -m app.cli scrape --source imf                # debt, fiscal balance + gap-fill
python -m app.cli scrape --source who                # adult obesity
python -m app.cli create-key --email you@example.com --tier pro

uvicorn app.main:app --reload                        # http://localhost:8000/docs
```

```bash
cd frontend
npm install
cp .env.example .env.local
npm run dev                                          # http://localhost:3000
```

Paste your key into the dashboard at `/dashboard`, then open `/explorer`.

## Quick start (Docker)

```bash
docker compose up --build
# API      http://localhost:8000/docs
# GraphQL  http://localhost:8000/graphql
# Frontend http://localhost:3000
docker compose exec api python -m app.cli scrape --source all
```

The `api` container runs `alembic upgrade head` and seeds reference data on boot. `worker` + `beat` re-scrape every source weekly (Sunday 02:00–04:00 UTC).

## API overview

Base URL `/v1`. Every endpoint except `/`, `/health`, `/docs` and `POST /v1/auth/register` needs an `X-API-Key` header.

| Endpoint | Purpose |
|---|---|
| `POST /auth/register` · `GET /auth/me` | Get a free key · see tier and current-hour usage |
| `GET /countries[?region=&sort=&order=]` · `GET /countries/{iso2}` | 54 countries with capital, currency, area, languages, latest population |
| `GET /indicators[?category=]` · `GET /indicators/{code}` | 87 indicators with unit, upstream source and original source code |
| `GET /data/{iso2}/{code}[?from=&to=&latest=]` | Time series for one country + indicator |
| `GET /data/{iso2}[?category=]` | Country snapshot: latest value of every indicator |
| `GET /compare?countries=&indicator=[&year=]` | Ranked comparison with continental average/total across **all** of Africa |
| `GET /compare/trend?countries=&indicator=[&from=&to=]` | Aligned multi-country time series |
| `GET /regions` · `GET /regions/{region}/summary[?category=]` | Five AU regions; per-region sums (GDP, population…) and means (rates, ratios) |
| `POST /graphql` | Same data, GraphQL. GraphiQL playground at `GET /graphql` |

Responses carry `X-RateLimit-Limit/Remaining/Reset`, `X-Cache: HIT|MISS` and `X-Response-Time`.

### Tiers

| | Free | Pro | Enterprise |
|---|---|---|---|
| Requests / hour | 100 | 5,000 | 100,000 |
| History | 2000 → | 1960 → | 1960 → |
| Compare countries | 5 | 54 | 54 |

Tier rules are enforced server-side (`app/models/api_user.py`). Change a user's tier with `python -m app.cli set-tier --email … --tier pro`.

## Data pipeline

```
World Bank WDI ──┐
IMF WEO ─────────┤   scrapers/*.py  ──▶  upsert (diff per indicator)  ──▶  data_points
WHO GHO ─────────┤   Observation(iso2, code, year, value)              (unique country+indicator+year)
UN WPP ──────────┘
```

* **World Bank** (primary, ~80 indicators): one `country/all` call per indicator, filtered to Africa client-side. Listing 54 ISO codes in the URL trips the World Bank WAF (403), so don't.
* **IMF DataMapper**: primary for `GOVERNMENT_DEBT_GDP` and `FISCAL_BALANCE_GDP`; gap-fills GDP growth, inflation, current account, GDP per capita and unemployment where WDI is missing. Never overwrites a World Bank value. Projection years are dropped.
* **WHO GHO**: `OBESITY_ADULT` (both sexes, age-standardized).
* **UN Population Division**: `MEDIAN_AGE`. Requires a free bearer token in `UN_DATA_API_TOKEN`; skips cleanly without one.
* **AfDB**: documented extension point (`scrapers/afdb.py`) — no free machine-readable feed exists today.

Source precedence when two feeds report the same point: World Bank = WHO = UN > IMF > AfDB.

Three indicators (`MOBILE_MONEY_ACCOUNTS_PCT`, `MICROFINANCE_BORROWERS`, `INSURANCE_PENETRATION`) are defined in the catalogue but have no free upstream feed yet; they're ready for national-bureau data without a schema change.

## Project layout

```
backend/app/
├── main.py              FastAPI app, middleware order, exception handlers
├── config.py            pydantic-settings (env / .env)
├── database.py          engine, SessionLocal, Base
├── models/              SQLAlchemy 2.0 ORM: Country, Indicator, DataPoint, ApiUser, RequestLog
├── schemas/             Pydantic response models
├── services/            data_service.py — query logic shared by REST and GraphQL
├── routers/             countries, indicators, data, compare, regions, auth
├── graphql/             Strawberry types, resolvers, schema
├── middleware/          api_key_auth, rate_limiter, response_cache, request_logger
├── scrapers/            base (upsert engine), world_bank, imf, who, un_data, afdb, scheduler (Celery)
├── utils/               cache (Redis / memory), security (key hashing), normalizer, seeds
└── cli.py               seed · scrape · create-key · rotate-key · set-tier · stats
```

## Testing

```bash
cd backend && python -m pytest -q      # 53 tests, ~6s, fully offline (SQLite + mocked upstreams)
cd frontend && npm run lint && npm run build
```

## Configuration

See [backend/.env.example](backend/.env.example) and [frontend/.env.example](frontend/.env.example). Notable switches:

| Variable | Default | Notes |
|---|---|---|
| `DATABASE_URL` | `sqlite:///./africadata.db` | Use `postgresql+psycopg://…` in Docker/production |
| `REDIS_URL` | *(empty)* | Empty → in-process cache (single instance only) |
| `AUTO_CREATE_TABLES` | `true` | Set `false` in production; run `alembic upgrade head` instead |
| `REQUIRE_API_KEY` | `true` | `false` lets anonymous calls through as free tier for local hacking |
| `UN_DATA_API_TOKEN` | *(empty)* | Needed for `MEDIAN_AGE` |

## Deploying (free tier)

* **API** → Railway or Render: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`, plus a worker service running `celery -A app.scrapers.scheduler worker -B`.
* **Database** → Supabase Postgres (`DATABASE_URL=postgresql+psycopg://…`), run `alembic upgrade head` once.
* **Cache** → Upstash Redis (`REDIS_URL=rediss://…`).
* **Frontend** → Vercel, set `NEXT_PUBLIC_API_URL` and `NEXT_PUBLIC_GRAPHQL_URL`; set `CORS_ORIGINS` on the API to the Vercel domain.

## Design notes / deviations from the spec

* **API keys are stored hashed** (SHA-256) with a display prefix; the raw key is shown once. The spec stored plaintext.
* **`languages` is JSON, not `TEXT[]`**, and `ip_address` is a string — keeps the schema portable across Postgres and SQLite.
* **Added `Indicator.aggregation`** (`sum` | `mean`) so regional roll-ups and continental totals are correct for both absolute values and rates.
* **Continental average/total** use every African country with data, not just the ones being compared — that's what makes the number meaningful.
* **Seychelles (SC) added**: the spec's ISO list had 53 codes.
* **NextAuth.js dropped**: the dashboard is API-key based; the key lives in the browser's localStorage. Adding a proper account system is a clean next step.
* **`/v1/regions` implemented** (was listed but had no code in the spec).
* **Response cache and rate limits fall back to memory** when Redis is absent so the project runs with zero infrastructure.

## Contact

| | |
|---|---|
| Email | [Keneansufa@gmail.com](mailto:Keneansufa@gmail.com) |
| Telegram | [@KeneanDita](https://t.me/KeneanDita) |
| WhatsApp | [+251 923 759 696](https://wa.me/251923759696) |
| Web | [keneandita.me](https://keneandita.me) |

## License

[MIT](LICENSE)
