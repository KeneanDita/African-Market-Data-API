import uuid
from datetime import datetime

from sqlalchemy import DateTime, Integer, String, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base

TIER_LIMITS: dict[str, int] = {
    "free": 100,
    "pro": 5000,
    "enterprise": 100_000,
}

TIER_MAX_COMPARE: dict[str, int] = {"free": 5, "pro": 54, "enterprise": 54}
TIER_MIN_YEAR: dict[str, int] = {"free": 2000, "pro": 1960, "enterprise": 1960}


class ApiUser(Base):
    __tablename__ = "api_users"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    name: Mapped[str | None] = mapped_column(String(200))
    # Only a SHA-256 hash of the key is stored; the raw key is shown once at registration.
    api_key_hash: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    key_prefix: Mapped[str] = mapped_column(String(16), nullable=False)
    tier: Mapped[str] = mapped_column(String(20), nullable=False, default="free")
    rate_limit: Mapped[int] = mapped_column(Integer, nullable=False, default=TIER_LIMITS["free"])
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    last_seen_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
