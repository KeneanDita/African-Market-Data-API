import os
from decimal import Decimal

# Must be set before `app` is imported: settings and the engine are created at import time.
os.environ.update({
    "DATABASE_URL": "sqlite://",
    "REDIS_URL": "",
    "ENVIRONMENT": "test",
    "LOG_REQUESTS": "true",
    "REQUIRE_API_KEY": "true",
    "AUTO_CREATE_TABLES": "true",
})

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

import app.models  # noqa: E402,F401
from app.database import Base, SessionLocal, engine  # noqa: E402
from app.main import app  # noqa: E402
from app.models.country import Country  # noqa: E402
from app.models.data_point import DataPoint  # noqa: E402
from app.models.indicator import Indicator  # noqa: E402
from app.utils.cache import reset_cache  # noqa: E402
from app.utils.countries_seed import seed_countries  # noqa: E402
from app.utils.indicators_seed import seed_indicators  # noqa: E402

# (iso2, indicator, {year: value})
SAMPLE_DATA = {
    ("ET", "GDP_CURRENT_USD"): {1995: 7.6e9, 2019: 95.9e9, 2020: 107.6e9, 2021: 111.3e9, 2022: 126.8e9, 2023: 163.7e9},
    ("NG", "GDP_CURRENT_USD"): {2019: 448.1e9, 2020: 432.2e9, 2021: 440.8e9, 2022: 477.4e9, 2023: 363.8e9},
    ("KE", "GDP_CURRENT_USD"): {2019: 100.4e9, 2020: 100.7e9, 2021: 109.7e9, 2022: 113.7e9, 2023: 107.4e9},
    ("ZA", "GDP_CURRENT_USD"): {2019: 389.3e9, 2020: 338.0e9, 2021: 420.1e9, 2022: 405.3e9},  # no 2023 on purpose
    ("ET", "POPULATION_TOTAL"): {2022: 123_379_924, 2023: 126_527_060},
    ("NG", "POPULATION_TOTAL"): {2022: 218_541_212, 2023: 223_804_632},
    ("KE", "POPULATION_TOTAL"): {2023: 55_100_586},
    ("ET", "INFLATION_ANNUAL"): {2021: 26.8, 2022: 33.9, 2023: 30.2},
    ("KE", "INFLATION_ANNUAL"): {2021: 6.1, 2022: 7.6, 2023: 7.7},
}


@pytest.fixture(scope="session")
def _schema():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        seed_countries(db)
        seed_indicators(db)
        countries = {c.iso2: c for c in db.query(Country).all()}
        indicators = {i.code: i for i in db.query(Indicator).all()}
        for (iso2, code), series in SAMPLE_DATA.items():
            for year, value in series.items():
                db.add(DataPoint(country_id=countries[iso2].id, indicator_id=indicators[code].id, year=year, value=Decimal(str(value)), source="World Bank"))
        db.commit()
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(autouse=True)
def _fresh_cache():
    reset_cache()
    yield
    reset_cache()


@pytest.fixture(scope="session")
def client(_schema):
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="session")
def api_key(client) -> str:
    resp = client.post("/v1/auth/register", json={"email": "tester@example.com", "name": "Tester"})
    assert resp.status_code == 201, resp.text
    return resp.json()["api_key"]


@pytest.fixture
def headers(api_key) -> dict:
    return {"X-API-Key": api_key}


@pytest.fixture
def db():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
