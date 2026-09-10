from datetime import datetime

from sqlalchemy import DateTime, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Indicator(Base):
    __tablename__ = "indicators"

    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    category: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    subcategory: Mapped[str | None] = mapped_column(String(50))
    unit: Mapped[str | None] = mapped_column(String(50))
    description: Mapped[str | None] = mapped_column(Text)
    source: Mapped[str | None] = mapped_column(String(100))
    source_code: Mapped[str | None] = mapped_column(String(100))
    # How to roll the indicator up across countries: "sum" for absolute totals, "mean" for rates/ratios.
    aggregation: Mapped[str] = mapped_column(String(10), nullable=False, default="mean")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    data_points = relationship("DataPoint", back_populates="indicator", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Indicator {self.code}>"
