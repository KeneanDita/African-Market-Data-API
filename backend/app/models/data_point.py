from datetime import datetime
from decimal import Decimal

from sqlalchemy import BigInteger, DateTime, ForeignKey, Index, Integer, Numeric, SmallInteger, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

BigIntPK = BigInteger().with_variant(Integer, "sqlite")


class DataPoint(Base):
    __tablename__ = "data_points"
    __table_args__ = (
        UniqueConstraint("country_id", "indicator_id", "year", name="uq_data_point"),
        Index("idx_data_points_country_indicator", "country_id", "indicator_id"),
        Index("idx_data_points_year", "year"),
    )

    id: Mapped[int] = mapped_column(BigIntPK, primary_key=True, autoincrement=True)
    country_id: Mapped[int] = mapped_column(ForeignKey("countries.id", ondelete="CASCADE"), nullable=False)
    indicator_id: Mapped[int] = mapped_column(ForeignKey("indicators.id", ondelete="CASCADE"), nullable=False)
    year: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    value: Mapped[Decimal | None] = mapped_column(Numeric(20, 6))
    source: Mapped[str | None] = mapped_column(String(100))
    scraped_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    country = relationship("Country", back_populates="data_points")
    indicator = relationship("Indicator", back_populates="data_points")
