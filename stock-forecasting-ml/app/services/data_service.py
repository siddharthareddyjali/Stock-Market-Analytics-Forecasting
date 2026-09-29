from __future__ import annotations

import logging
import time
from datetime import datetime

import pandas as pd
import yfinance as yf
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.stock import Stock
from app.models.stock_price import StockPrice
from app.services.stock_service import StockService

logger = logging.getLogger(__name__)


def _clean_price_frame(frame: pd.DataFrame) -> pd.DataFrame:
    if frame is None or frame.empty:
        raise ValueError("Yahoo Finance returned no data.")

    clean = frame.copy()
    if isinstance(clean.columns, pd.MultiIndex):
        expected_columns = {"Open", "High", "Low", "Close", "Adj Close", "Volume"}
        clean.columns = [
            next((part for part in column if part in expected_columns), column[-1])
            for column in clean.columns
        ]
    clean.index = pd.to_datetime(clean.index)
    clean = clean.rename(columns={
        "Open": "open_price",
        "High": "high_price",
        "Low": "low_price",
        "Close": "close_price",
        "Adj Close": "adjusted_close",
        "Volume": "volume",
    })
    if "close_price" not in clean.columns:
        raise ValueError("Yahoo Finance response is missing closing prices.")

    clean = clean.loc[:, [col for col in ["open_price", "high_price", "low_price", "close_price", "adjusted_close", "volume"] if col in clean.columns]]
    clean = clean[~clean.index.duplicated(keep="last")]
    clean = clean.sort_index()
    clean = clean.ffill().bfill()
    clean = clean.dropna(subset=["close_price"])
    clean["trade_date"] = clean.index.date
    return clean


def _download_history(ticker: str) -> pd.DataFrame:
    last_error: Exception | None = None
    for attempt in range(1, 4):
        try:
            history = yf.download(
                tickers=ticker,
                period="10y",
                interval="1d",
                auto_adjust=False,
                actions=False,
                progress=False,
                threads=False,
                timeout=30,
            )
            if history is not None and not history.empty:
                return history
            logger.warning("Yahoo Finance returned no data for %s on attempt %s", ticker, attempt)
        except Exception as exc:
            last_error = exc
            logger.warning("Yahoo Finance download attempt %s failed for %s: %s", attempt, ticker, exc)
        if attempt < 3:
            time.sleep(attempt)

    try:
        logger.info("Trying Yahoo Finance Ticker.history fallback for %s", ticker)
        history = yf.Ticker(ticker).history(
            period="10y",
            interval="1d",
            auto_adjust=False,
            actions=False,
            timeout=30,
        )
        if history is not None and not history.empty:
            return history
    except Exception as exc:
        last_error = exc
        logger.warning("Yahoo Finance history fallback failed for %s: %s", ticker, exc)

    if last_error is not None:
        raise RuntimeError("Unable to download stock data from Yahoo Finance.") from last_error
    raise ValueError("No historical data returned for this ticker.")


def _upsert_price_rows(db: Session, stock_id: int, frame: pd.DataFrame) -> None:
    for _, row in frame.iterrows():
        trade_date = row["trade_date"]
        existing = db.execute(
            select(StockPrice).where(StockPrice.stock_id == stock_id, StockPrice.trade_date == trade_date)
        ).scalar_one_or_none()
        if existing is None:
            db.add(StockPrice(
                stock_id=stock_id,
                trade_date=trade_date,
                open_price=float(row.get("open_price")) if pd.notna(row.get("open_price")) else None,
                high_price=float(row.get("high_price")) if pd.notna(row.get("high_price")) else None,
                low_price=float(row.get("low_price")) if pd.notna(row.get("low_price")) else None,
                close_price=float(row.get("close_price")) if pd.notna(row.get("close_price")) else None,
                adjusted_close=float(row.get("adjusted_close")) if pd.notna(row.get("adjusted_close")) else None,
                volume=int(row.get("volume")) if pd.notna(row.get("volume")) else None,
            ))
        else:
            existing.open_price = float(row.get("open_price")) if pd.notna(row.get("open_price")) else None
            existing.high_price = float(row.get("high_price")) if pd.notna(row.get("high_price")) else None
            existing.low_price = float(row.get("low_price")) if pd.notna(row.get("low_price")) else None
            existing.close_price = float(row.get("close_price")) if pd.notna(row.get("close_price")) else None
            existing.adjusted_close = float(row.get("adjusted_close")) if pd.notna(row.get("adjusted_close")) else None
            existing.volume = int(row.get("volume")) if pd.notna(row.get("volume")) else None
    db.commit()


def get_historical_price_data(db: Session, ticker: str) -> pd.DataFrame:
    stock = StockService.get_or_create_stock(db, ticker)
    rows = db.execute(select(StockPrice).where(StockPrice.stock_id == stock.id).order_by(StockPrice.trade_date.asc())).scalars().all()

    if rows:
        latest_date = max(item.trade_date for item in rows)
        age_days = (datetime.utcnow().date() - latest_date).days
        if age_days <= 7 and len(rows) >= 150:
            logger.info("Database cache hit for %s with %s rows", ticker, len(rows))
            prices = pd.DataFrame([
                {
                    "Date": item.trade_date,
                    "Open": item.open_price,
                    "High": item.high_price,
                    "Low": item.low_price,
                    "Close": item.close_price,
                    "Adj Close": item.adjusted_close,
                    "Volume": item.volume,
                }
                for item in rows
            ])
            if not prices.empty:
                prices = prices.set_index("Date")
                prices.index = pd.to_datetime(prices.index)
                return prices.sort_index()

    logger.info("Database cache miss for %s, downloading recent historical data", ticker)
    history = _download_history(ticker)
    cleaned = _clean_price_frame(history)
    _upsert_price_rows(db, stock.id, cleaned)
    return cleaned.set_index("trade_date").sort_index()
