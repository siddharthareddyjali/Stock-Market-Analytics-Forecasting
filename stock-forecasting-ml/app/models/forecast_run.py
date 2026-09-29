from __future__ import annotations

from datetime import datetime

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class ForecastRun(Base):
    __tablename__ = "forecast_runs"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    stock_id: Mapped[int] = mapped_column(ForeignKey("stocks.id"), nullable=False, index=True)
    forecast_days: Mapped[int] = mapped_column(nullable=False)
    current_price: Mapped[float] = mapped_column(nullable=False)
    predicted_price: Mapped[float] = mapped_column(nullable=False)
    predicted_change: Mapped[float] = mapped_column(nullable=False)
    predicted_change_percent: Mapped[float] = mapped_column(nullable=False)
    created_at: Mapped[datetime] = mapped_column(nullable=False, default=datetime.utcnow)

    stock = relationship("Stock", back_populates="forecast_runs")
    predictions = relationship("ForecastPrediction", back_populates="forecast_run", cascade="all, delete-orphan")
    metrics = relationship("ModelMetric", back_populates="forecast_run", cascade="all, delete-orphan")
    weights = relationship("ModelWeight", back_populates="forecast_run", cascade="all, delete-orphan")
