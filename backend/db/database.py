from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.base import Base

DATABASE_URL = "sqlite:///./citations.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

LocalSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)
