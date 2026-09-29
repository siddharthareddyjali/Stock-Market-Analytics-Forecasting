from pydantic import BaseModel, Field, field_validator


class StockRequest(BaseModel):
    ticker: str = Field(..., min_length=1, max_length=20)

    @field_validator("ticker")
    @classmethod
    def validate_ticker(cls, value: str) -> str:
        normalized = value.strip().upper()
        if not normalized or not normalized.replace(".", "").replace("-", "").isalnum():
            raise ValueError("Ticker must contain letters, numbers, dots, or dashes only.")
        return normalized


class StockResponse(BaseModel):
    id: int
    ticker: str
    company_name: str | None = None
    exchange: str | None = None
    currency: str | None = None
