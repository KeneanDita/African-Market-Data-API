from datetime import datetime

from sqlalchemy import BigInteger, DateTime, Index, Integer, SmallInteger, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base

BigIntPK = BigInteger().with_variant(Integer, "sqlite")


class RequestLog(Base):
    __tablename__ = "request_logs"
    __table_args__ = (Index("idx_request_logs_api_key_created", "api_key_hash", "created_at"),)

    id: Mapped[int] = mapped_column(BigIntPK, primary_key=True, autoincrement=True)
    api_key_hash: Mapped[str | None] = mapped_column(String(64))
    endpoint: Mapped[str | None] = mapped_column(String(200))
    method: Mapped[str | None] = mapped_column(String(10))
    status_code: Mapped[int | None] = mapped_column(SmallInteger)
    response_ms: Mapped[int | None] = mapped_column(Integer)
    ip_address: Mapped[str | None] = mapped_column(String(45))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
