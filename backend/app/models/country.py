from datetime import datetime

from sqlalchemy import JSON, BigInteger, DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Country(Base):
    __tablename__ = "countries"

    id: Mapped[int] = mapped_column(primary_key=True)
    iso2: Mapped[str] = mapped_column(String(2), unique=True, nullable=False, index=True)
    iso3: Mapped[str] = mapped_column(String(3), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    region: Mapped[str | None] = mapped_column(String(50), index=True)
    capital: Mapped[str | None] = mapped_column(String(100))
    currency: Mapped[str | None] = mapped_column(String(50))
    currency_code: Mapped[str | None] = mapped_column(String(3))
    population: Mapped[int | None] = mapped_column(BigInteger)
    area_km2: Mapped[int | None] = mapped_column(BigInteger)
    # JSON instead of TEXT[] so the schema works on both PostgreSQL and SQLite.
    languages: Mapped[list[str] | None] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    data_points = relationship("DataPoint", back_populates="country", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Country {self.iso2} {self.name}>"
