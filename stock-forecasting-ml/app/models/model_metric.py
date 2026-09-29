from __future__ import annotations

from datetime import datetime

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class ModelMetric(Base):
    __tablename__ = "model_metrics"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    forecast_run_id: Mapped[int] = mapped_column(ForeignKey("forecast_runs.id"), nullable=False, index=True)
    model_name: Mapped[str] = mapped_column(String(50), nullable=False)
    mae: Mapped[float | None] = mapped_column(nullable=True)
    rmse: Mapped[float | None] = mapped_column(nullable=True)
    mape: Mapped[float | None] = mapped_column(nullable=True)
    created_at: Mapped[datetime] = mapped_column(nullable=False, default=datetime.utcnow)

    forecast_run = relationship("ForecastRun", back_populates="metrics")
