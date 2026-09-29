import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parents[2]
load_dotenv(BASE_DIR / ".env")


def _get_database_url() -> str:
    value = os.getenv("DATABASE_URL")
    if value:
        return value
    return "mysql+pymysql://user:password@localhost:3306/stock_forecasting"


class Settings:
    APP_TITLE = "Stock Market Analytics & Forecasting"
    APP_VERSION = "1.0.0"
    DEBUG = os.getenv("DEBUG", "false").lower() == "true"
    DATABASE_URL = _get_database_url()
    FRONTEND_DIR = BASE_DIR / "frontend"
    ARTIFACTS_DIR = BASE_DIR / "artifacts"
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")


settings = Settings()
