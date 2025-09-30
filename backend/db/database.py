from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from models.base import Base
from typing import Generator

DATABASE_URL = "sqlite:///./citations.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

LocalSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db() -> Generator[Session, None, None]:
    """Database session generator for FastAPI dependency injection."""
    db = LocalSession()
    try:
        yield db
    finally:
        db.close()
