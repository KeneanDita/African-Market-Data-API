from functools import lru_cache

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "African Market Data API"
    version: str = "1.0.0"
    environment: str = "development"  # development | test | production
    secret_key: str = "change-me-in-production"
    api_base_url: str = "http://localhost:8000"
    docs_url: str = "https://africadata.dev/docs"

    # SQLite by default so the project runs with zero setup; use Postgres in docker/prod.
    database_url: str = "sqlite:///./africadata.db"
    auto_create_tables: bool = True

    # Optional. When unset/unreachable the app falls back to an in-process cache.
    redis_url: str | None = None
    cache_ttl_seconds: int = 3600

    require_api_key: bool = True
    log_requests: bool = True
    cors_origins: str = "*"
    # Protects /v1/admin/* (remote scrape trigger). Unset = admin routes disabled.
    admin_token: str | None = None

    scrape_from_year: int = 1960
    scrape_to_year: int = 2025
    un_data_api_token: str | None = None

    smtp_host: str | None = None
    smtp_port: int = 587
    smtp_user: str | None = None
    smtp_pass: str | None = None

    @field_validator("redis_url", "un_data_api_token", "smtp_host", "smtp_user", "smtp_pass", "admin_token", mode="before")
    @classmethod
    def _empty_to_none(cls, v):
        return v or None

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @property
    def is_sqlite(self) -> bool:
        return self.database_url.startswith("sqlite")


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
