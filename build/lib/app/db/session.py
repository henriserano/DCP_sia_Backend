from __future__ import annotations

import os
from typing import Generator, Optional

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.core.config import get_settings

Base = declarative_base()

# SQLite by default (simple local), can be overridden by env var DATABASE_URL
# Examples:
#   sqlite:///./data/app.db
#   postgresql+psycopg2://user:pass@localhost:5432/dcp_eval
def _build_database_url() -> str:
    settings = get_settings()
    url = os.getenv("DATABASE_URL")
    if url:
        return url

    # default sqlite
    os.makedirs("data", exist_ok=True)
    return "sqlite:///./data/app.db"


DATABASE_URL = _build_database_url()

# SQLite needs special flag for multithread (uvicorn reload/dev)
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    connect_args=connect_args,
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def init_db() -> None:
    """Create tables (POC). For prod, use Alembic migrations."""
    Base.metadata.create_all(bind=engine)


def get_db() -> Generator:
    """FastAPI dependency."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()