"""initial schema

Revision ID: 0001_initial
Revises:
Create Date: 2026-09-10
"""
from alembic import op
import sqlalchemy as sa

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None

BigIntPK = sa.BigInteger().with_variant(sa.Integer, "sqlite")


def upgrade() -> None:
    op.create_table(
        "countries",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("iso2", sa.String(2), nullable=False),
        sa.Column("iso3", sa.String(3), nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("region", sa.String(50)),
        sa.Column("capital", sa.String(100)),
        sa.Column("currency", sa.String(50)),
        sa.Column("currency_code", sa.String(3)),
        sa.Column("population", sa.BigInteger),
        sa.Column("area_km2", sa.BigInteger),
        sa.Column("languages", sa.JSON),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint("iso2", name="uq_countries_iso2"),
        sa.UniqueConstraint("iso3", name="uq_countries_iso3"),
    )
    op.create_index("ix_countries_iso2", "countries", ["iso2"])
    op.create_index("ix_countries_region", "countries", ["region"])

    op.create_table(
        "indicators",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("code", sa.String(50), nullable=False),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("category", sa.String(50), nullable=False),
        sa.Column("subcategory", sa.String(50)),
        sa.Column("unit", sa.String(50)),
        sa.Column("description", sa.Text),
        sa.Column("source", sa.String(100)),
        sa.Column("source_code", sa.String(100)),
        sa.Column("aggregation", sa.String(10), nullable=False, server_default="mean"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint("code", name="uq_indicators_code"),
    )
    op.create_index("ix_indicators_code", "indicators", ["code"])
    op.create_index("ix_indicators_category", "indicators", ["category"])

    op.create_table(
        "data_points",
        sa.Column("id", BigIntPK, primary_key=True, autoincrement=True),
        sa.Column("country_id", sa.Integer, sa.ForeignKey("countries.id", ondelete="CASCADE"), nullable=False),
        sa.Column("indicator_id", sa.Integer, sa.ForeignKey("indicators.id", ondelete="CASCADE"), nullable=False),
        sa.Column("year", sa.SmallInteger, nullable=False),
        sa.Column("value", sa.Numeric(20, 6)),
        sa.Column("source", sa.String(100)),
        sa.Column("scraped_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint("country_id", "indicator_id", "year", name="uq_data_point"),
    )
    op.create_index("idx_data_points_country_indicator", "data_points", ["country_id", "indicator_id"])
    op.create_index("idx_data_points_year", "data_points", ["year"])

    op.create_table(
        "api_users",
        sa.Column("id", sa.Uuid, primary_key=True),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("name", sa.String(200)),
        sa.Column("api_key_hash", sa.String(64), nullable=False),
        sa.Column("key_prefix", sa.String(16), nullable=False),
        sa.Column("tier", sa.String(20), nullable=False, server_default="free"),
        sa.Column("rate_limit", sa.Integer, nullable=False, server_default="100"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("last_seen_at", sa.DateTime(timezone=True)),
        sa.UniqueConstraint("email", name="uq_api_users_email"),
        sa.UniqueConstraint("api_key_hash", name="uq_api_users_key_hash"),
    )
    op.create_index("ix_api_users_api_key_hash", "api_users", ["api_key_hash"])

    op.create_table(
        "request_logs",
        sa.Column("id", BigIntPK, primary_key=True, autoincrement=True),
        sa.Column("api_key_hash", sa.String(64)),
        sa.Column("endpoint", sa.String(200)),
        sa.Column("method", sa.String(10)),
        sa.Column("status_code", sa.SmallInteger),
        sa.Column("response_ms", sa.Integer),
        sa.Column("ip_address", sa.String(45)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("idx_request_logs_api_key_created", "request_logs", ["api_key_hash", "created_at"])


def downgrade() -> None:
    op.drop_table("request_logs")
    op.drop_table("api_users")
    op.drop_table("data_points")
    op.drop_table("indicators")
    op.drop_table("countries")
