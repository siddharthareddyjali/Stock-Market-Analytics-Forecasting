import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import text

from app.core.config import settings
from app.core.database import init_db
from app.models.stock import Stock
from app.schemas.forecast import ForecastRequest
from app.services.data_service import get_historical_price_data
from app.services.forecast_service import ForecastService
from app.services.stock_service import StockService
from app.utils.validators import is_valid_forecast_days, is_valid_ticker

logging.basicConfig(level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO))
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        init_db()
        logger.info("Application startup complete.")
    except Exception as exc:
        logger.exception("Startup database check failed: %s", exc)
    yield


app = FastAPI(title=settings.APP_TITLE, version=settings.APP_VERSION, lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/css", StaticFiles(directory=str(settings.FRONTEND_DIR / "css")), name="css")
app.mount("/js", StaticFiles(directory=str(settings.FRONTEND_DIR / "js")), name="js")


@app.get("/health")
def health_check():
    try:
        from app.core.database import engine
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return {"status": "ok", "database": "connected", "version": settings.APP_VERSION}
    except Exception as exc:
        logger.exception("Health endpoint failed: %s", exc)
        return {"status": "degraded", "database": "unavailable", "version": settings.APP_VERSION}


@app.get("/")
def index():
    return FileResponse(str(settings.FRONTEND_DIR / "index.html"))


@app.get("/api/stocks")
def get_stocks():
    from app.core.database import SessionLocal

    db = SessionLocal()
    try:
        stocks = db.query(Stock).order_by(Stock.ticker.asc()).all()
        return [{"ticker": item.ticker, "company_name": item.company_name, "exchange": item.exchange, "currency": item.currency} for item in stocks]
    finally:
        db.close()


@app.get("/api/forecast")
def generate_forecast_endpoint(ticker: str = Query(..., min_length=1), forecast_days: int = Query(..., ge=1)):
    if not is_valid_ticker(ticker):
        raise HTTPException(status_code=400, detail="Invalid ticker.")
    if not is_valid_forecast_days(forecast_days):
        raise HTTPException(status_code=400, detail="Forecast period must be one of 7, 15, 30, 60, 90 days.")

    from app.core.database import SessionLocal

    db = SessionLocal()
    try:
        history = get_historical_price_data(db, ticker)
        forecast_service = ForecastService(forecast_days=forecast_days)
        result = forecast_service.generate_forecast(history)
        return {
            "ticker": ticker.upper(),
            "current_price": result["current_price"],
            "forecast_days": forecast_days,
            "predicted_price": result["predicted_price"],
            "predicted_change": result["predicted_change"],
            "predicted_change_percent": result["predicted_change_percent"],
            "histories": [{"date": ts.date().isoformat(), "close": float(value)} for ts, value in result["series"].items()],
            "forecast_points": result["forecast_rows"],
            "model_metrics": [{"model_name": name, "mae": metrics["mae"], "rmse": metrics["rmse"], "mape": metrics["mape"]} for name, metrics in result["metrics"].items()],
            "model_weights": [{"model_name": name, "weight": weight} for name, weight in result["weights"].items()],
        }
    except ValueError as exc:
        logger.exception("Forecast generation failed for %s: %s", ticker, exc)
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("Unexpected forecast failure for %s: %s", ticker, exc)
        raise HTTPException(status_code=500, detail="Forecast generation failed. Please try again.") from exc
    finally:
        db.close()


@app.get("/api/forecast-history")
def forecast_history():
    from app.core.database import SessionLocal

    db = SessionLocal()
    try:
        # placeholder for recent forecasts listing, kept lightweight for the dashboard
        return []
    finally:
        db.close()
