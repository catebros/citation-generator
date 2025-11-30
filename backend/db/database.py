# backend/db/database.py
import os
from typing import Generator

from dotenv import load_dotenv
from models.base import Base  # noqa: F401 - imported for metadata
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

load_dotenv()

# Get DATABASE_URL from environment - fail fast if not set
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError(
        "DATABASE_URL environment variable is not set.\n"
        "Please set it in your .env file or environment.\n"
        "Example: DATABASE_URL=postgresql://postgres:postgres@localhost:5432/citation_generator_db\n"
        "For local development, copy .env.example to .env and configure your database URL."
    )


class DatabaseEngine:
    """
    Singleton class for managing the SQLAlchemy database engine.
    """

    _instance = None
    _engine = None

    def __new__(cls):
        """
        Creates or returns the existing singleton instance.
        """
        if cls._instance is None:
            cls._instance = super(DatabaseEngine, cls).__new__(cls)
        return cls._instance

    def get_engine(self):
        """
        Get the SQLAlchemy engine, creating it if it doesn't exist.
        """
        if self._engine is None:
            # PostgreSQL connection without special arguments
            self._engine = create_engine(DATABASE_URL)
        return self._engine

    @classmethod
    def reset_instance(cls):
        """
        Reset the singleton instance (useful for testing).
        """
        # Dispose of the old engine if it exists
        if cls._instance is not None and cls._instance._engine is not None:
            cls._instance._engine.dispose()

        # Reset both instance and engine
        cls._instance = None
        if hasattr(cls, "_engine"):
            cls._engine = None


# Get the singleton engine instance
def get_singleton_engine():
    """Get the current singleton engine instance."""
    return DatabaseEngine().get_engine()


# Get the singleton engine
engine = get_singleton_engine()


# Session factory for creating database sessions
# autocommit=False: Manual transaction control (explicit commits required)
# autoflush=False: Manual flushing of changes to database
# bind=engine: Associates sessions with the singleton engine
def get_session_factory():
    """Get a session factory bound to the current singleton engine."""
    return sessionmaker(autocommit=False, autoflush=False, bind=get_singleton_engine())


LocalSession = get_session_factory()


def get_db() -> Generator[Session, None, None]:
    """
    Database session generator for FastAPI dependency injection.

    Creates a new database session for each request and ensures proper cleanup.
    Uses generator pattern to guarantee session closure even if exceptions occur.
    """
    # Create new database session using current session factory
    session_factory = get_session_factory()
    db = session_factory()
    try:
        # Yield session to the requesting function
        yield db
    finally:
        # Ensure session is always closed, even if an exception occurs
        db.close()
