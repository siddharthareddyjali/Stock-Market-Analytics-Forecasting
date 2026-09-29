import logging
from typing import Generator

from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, declarative_base, sessionmaker

from app.core.config import settings

logger = logging.getLogger(__name__)
Base = declarative_base()

connect_args = {"charset": "utf8mb4"} if settings.DATABASE_URL.startswith("mysql") else {}
engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True, future=True, echo=False, connect_args=connect_args if settings.DATABASE_URL.startswith("mysql") else {})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, expire_on_commit=False)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    try:
        with engine.begin() as conn:
            conn.execute(text("SELECT 1"))
        Base.metadata.create_all(bind=engine)
        logger.info("Database initialized successfully.")
    except Exception as exc:
        logger.exception("Database initialization failed: %s", exc)
        raise RuntimeError("Database is unavailable. Please configure MySQL and ensure it is running.") from exc


__all__ = ["Base", "SessionLocal", "engine", "get_db", "init_db"]
