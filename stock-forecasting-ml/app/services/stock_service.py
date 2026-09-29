from __future__ import annotations

import logging
from typing import Any

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.models.stock import Stock
from app.models.stock_price import StockPrice
from app.utils.validators import is_valid_ticker

logger = logging.getLogger(__name__)


class StockService:
    @staticmethod
    def get_or_create_stock(db: Session, ticker: str) -> Stock:
        normalized = ticker.strip().upper()
        if not is_valid_ticker(normalized):
            raise ValueError("Ticker is invalid.")

        stock = db.scalar(select(Stock).where(Stock.ticker == normalized))
        if stock is not None:
            return stock

        stock = Stock(ticker=normalized)
        db.add(stock)
        db.commit()
        db.refresh(stock)
        return stock

    @staticmethod
    def get_recent_forecasts(db: Session, limit: int = 10) -> list[dict[str, Any]]:
        try:
            rows = db.execute(
                select(Stock.ticker, StockPrice.close_price, StockPrice.trade_date).join(StockPrice, Stock.id == StockPrice.stock_id)
                .order_by(StockPrice.trade_date.desc())
                .limit(limit)
            ).all()
            return [
                {"ticker": ticker, "close_price": float(close_price), "trade_date": trade_date.isoformat()}
                for ticker, close_price, trade_date in rows
            ]
        except SQLAlchemyError as exc:
            logger.exception("Failed to load recent stock data: %s", exc)
            return []
