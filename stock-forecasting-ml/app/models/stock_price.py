from __future__ import annotations

from datetime import datetime

from sqlalchemy import Date, ForeignKey, Index, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class StockPrice(Base):
    __tablename__ = "stock_prices"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    stock_id: Mapped[int] = mapped_column(ForeignKey("stocks.id"), nullable=False, index=True)
    trade_date: Mapped[datetime] = mapped_column(Date, nullable=False, index=True)
    open_price: Mapped[float | None] = mapped_column(nullable=True)
    high_price: Mapped[float | None] = mapped_column(nullable=True)
    low_price: Mapped[float | None] = mapped_column(nullable=True)
    close_price: Mapped[float | None] = mapped_column(nullable=True)
    adjusted_close: Mapped[float | None] = mapped_column(nullable=True)
    volume: Mapped[int | None] = mapped_column(nullable=True)
    created_at: Mapped[datetime] = mapped_column(nullable=False, default=datetime.utcnow)

    stock = relationship("Stock", back_populates="prices")

    __table_args__ = (
        UniqueConstraint("stock_id", "trade_date", name="uq_stock_price_date"),
        Index("idx_stock_price_stock_date", "stock_id", "trade_date"),
    )
