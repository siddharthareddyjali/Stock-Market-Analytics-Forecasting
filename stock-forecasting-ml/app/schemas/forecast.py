from datetime import date

from pydantic import BaseModel, Field, field_validator

ALLOWED_FORECAST_DAYS = {7, 15, 30, 60, 90}


class ForecastRequest(BaseModel):
    ticker: str = Field(..., min_length=1, max_length=20)
    forecast_days: int = Field(..., gt=0)

    @field_validator("ticker")
    @classmethod
    def validate_ticker(cls, value: str) -> str:
        normalized = value.strip().upper()
        if not normalized or not normalized.replace(".", "").replace("-", "").isalnum():
            raise ValueError("Ticker must contain letters, numbers, dots, or dashes only.")
        return normalized

    @field_validator("forecast_days")
    @classmethod
    def validate_forecast_days(cls, value: int) -> int:
        if value not in ALLOWED_FORECAST_DAYS:
            raise ValueError("Forecast period must be one of: 7, 15, 30, 60, 90 days.")
        return value


class ForecastPoint(BaseModel):
    date: date
    arima_prediction: float | None = None
    random_forest_prediction: float | None = None
    lstm_prediction: float | None = None
    ensemble_prediction: float | None = None


class ModelMetricSchema(BaseModel):
    model_name: str = Field(..., alias="model_name")
    mae: float | None = None
    rmse: float | None = None
    mape: float | None = None

    model_config = {"protected_namespaces": ()}


class ModelWeightSchema(BaseModel):
    model_name: str = Field(..., alias="model_name")
    weight: float

    model_config = {"protected_namespaces": ()}


class ForecastResponse(BaseModel):
    ticker: str
    current_price: float
    forecast_days: int
    predicted_price: float
    predicted_change: float
    predicted_change_percent: float
    generated_at: str
    historical_points: list[dict]
    forecast_points: list[ForecastPoint]
    model_metrics: list[ModelMetricSchema] = Field(default_factory=list)
    model_weights: list[ModelWeightSchema] = Field(default_factory=list)

    model_config = {"protected_namespaces": ()}
