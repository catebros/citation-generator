# 
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from models.base import Base
from typing import Generator

# SQLite database URL - creates a local file-based database named 'citations.db'
DATABASE_URL = "sqlite:///./citations.db"

# Create SQLAlchemy engine with SQLite-specific configuration
# connect_args={"check_same_thread": False} allows multiple threads to use the same connection
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# Session factory for creating database sessions
# autocommit=False: Manual transaction control (explicit commits required)
# autoflush=False: Manual flushing of changes to database
# bind=engine: Associates sessions with the database engine
LocalSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db() -> Generator[Session, None, None]:
    """
    Database session generator for FastAPI dependency injection.
    
    Creates a new database session for each request and ensures proper cleanup.
    Uses generator pattern to guarantee session closure even if exceptions occur.
    
    Yields:
        Session: SQLAlchemy database session
        
    Usage:
        Used as a FastAPI dependency to inject database sessions into route handlers.
    """
    # Create new database session
    db = LocalSession()
    try:
        # Yield session to the requesting function
        yield db
    finally:
        # Ensure session is always closed, even if an exception occurs
        db.close()
