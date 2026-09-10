import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.database import Base, engine
from app.graphql.schema import graphql_router
from app.middleware.rate_limiter import RateLimiterMiddleware
from app.middleware.request_logger import RequestLoggerMiddleware
from app.middleware.response_cache import ResponseCacheMiddleware
from app.routers import admin, auth, compare, countries, data, indicators, regions
from app.services.data_service import BadRequest, NotFound
from app.utils.cache import get_cache

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger("app")

DESCRIPTION = """
The single source of truth for African economic & demographic data.

* **54 countries**, **87 indicators**, time series back to 1960 (2000+ on the free tier).
* REST under `/v1`, GraphQL at `/graphql`.
* Every request needs an `X-API-Key` header. Get a free key from `POST /v1/auth/register`.

Upstream sources: World Bank, IMF, WHO, UN Population Division.
"""


@asynccontextmanager
async def lifespan(app: FastAPI):
    if settings.auto_create_tables:
        # Alembic owns the schema in production; create_all keeps zero-config dev/test working.
        import app.models  # noqa: F401 - register models

        Base.metadata.create_all(bind=engine)
    logger.info("environment=%s db=%s cache=%s", settings.environment, engine.url.render_as_string(hide_password=True), get_cache().backend)
    yield


app = FastAPI(
    title=settings.app_name,
    description=DESCRIPTION,
    version=settings.version,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
    openapi_tags=[
        {"name": "Auth", "description": "Register and inspect your API key"},
        {"name": "Countries", "description": "Country metadata"},
        {"name": "Indicators", "description": "Indicator catalogue"},
        {"name": "Data", "description": "Time series and country snapshots"},
        {"name": "Compare", "description": "Cross-country rankings and trends"},
        {"name": "Regions", "description": "Regional aggregates"},
    ],
)

# Middleware runs outermost-last-added: CORS -> logger -> rate limiter/auth -> response cache -> routes.
app.add_middleware(ResponseCacheMiddleware)
app.add_middleware(RateLimiterMiddleware)
app.add_middleware(RequestLoggerMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-RateLimit-Limit", "X-RateLimit-Remaining", "X-RateLimit-Reset", "X-Cache", "X-Response-Time"],
)


@app.exception_handler(NotFound)
async def not_found_handler(_: Request, exc: NotFound):
    return JSONResponse(status_code=404, content={"detail": str(exc)})


@app.exception_handler(BadRequest)
async def bad_request_handler(_: Request, exc: BadRequest):
    return JSONResponse(status_code=400, content={"detail": str(exc)})


app.include_router(auth.router, prefix="/v1/auth", tags=["Auth"])
app.include_router(countries.router, prefix="/v1/countries", tags=["Countries"])
app.include_router(indicators.router, prefix="/v1/indicators", tags=["Indicators"])
app.include_router(data.router, prefix="/v1/data", tags=["Data"])
app.include_router(compare.router, prefix="/v1/compare", tags=["Compare"])
app.include_router(regions.router, prefix="/v1/regions", tags=["Regions"])
app.include_router(admin.router, prefix="/v1/admin", tags=["Admin"], include_in_schema=bool(settings.admin_token))
app.include_router(graphql_router, prefix="/graphql", tags=["GraphQL"])


@app.get("/", tags=["Meta"])
def root():
    return {
        "name": settings.app_name,
        "version": settings.version,
        "docs": "/docs",
        "redoc": "/redoc",
        "graphql": "/graphql",
        "register": "POST /v1/auth/register",
        "status": "operational",
    }


@app.get("/health", tags=["Meta"])
def health():
    from sqlalchemy import text

    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        db_ok = True
    except Exception:  # noqa: BLE001
        db_ok = False
    return {"status": "ok" if db_ok else "degraded", "database": "ok" if db_ok else "unreachable", "cache": get_cache().backend}
