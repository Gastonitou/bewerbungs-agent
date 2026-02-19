"""Database configuration and session management."""

import os
from contextlib import contextmanager
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from bewerbungs_agent.models import Base
from bewerbungs_agent.utils.config import get_settings

settings = get_settings()

# Create engine based on DATABASE_URL
engine = create_engine(
    settings.database_url,
    echo=settings.app_env == "development",
    pool_pre_ping=True,  # Verify connections before using
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    """Initialize database tables."""
    Base.metadata.create_all(bind=engine)


def drop_db():
    """Drop all database tables (use with caution!)."""
    Base.metadata.drop_all(bind=engine)


def get_db() -> Generator[Session, None, None]:
    """
    Dependency for getting database sessions.
    Use with context manager or FastAPI Depends.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def db_session() -> Generator[Session, None, None]:
    """Context manager for database sessions."""
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
