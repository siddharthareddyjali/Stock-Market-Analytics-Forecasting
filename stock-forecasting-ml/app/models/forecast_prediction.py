from __future__ import annotations

from datetime import datetime

from sqlalchemy import Date, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class ForecastPrediction(Base):
    __tablename__ = "forecast_predictions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    forecast_run_id: Mapped[int] = mapped_column(ForeignKey("forecast_runs.id"), nullable=False, index=True)
    forecast_date: Mapped[datetime] = mapped_column(Date, nullable=False, index=True)
    arima_prediction: Mapped[float | None] = mapped_column(nullable=True)
    random_forest_prediction: Mapped[float | None] = mapped_column(nullable=True)
    lstm_prediction: Mapped[float | None] = mapped_column(nullable=True)
    ensemble_prediction: Mapped[float | None] = mapped_column(nullable=True)

    forecast_run = relationship("ForecastRun", back_populates="predictions")
