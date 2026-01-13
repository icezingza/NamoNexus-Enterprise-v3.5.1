"""Database connection and session management."""

from __future__ import annotations

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker

from src.config import config


DATABASE_URL = config.DATABASE_URL

connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    echo=config.DEBUG,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db() -> Session:
    """Yield a database session for FastAPI dependencies."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """Create all tables (dev/testing convenience)."""
    from src.models import interaction, memory, user  # noqa: F401

    Base.metadata.create_all(bind=engine)
