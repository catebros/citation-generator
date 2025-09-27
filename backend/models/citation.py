from sqlalchemy import Column, Integer, String, Text, DateTime
from datetime import datetime, UTC
from models.base import Base

class Citation(Base):
    __tablename__ = "citations"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(String, nullable=False)  
    title = Column(String, nullable=False)
    authors = Column(Text, nullable=False)  
    year = Column(Integer, nullable=False)
    publisher = Column(String, nullable=True)
    journal = Column(String, nullable=True)
    volume = Column(String, nullable=True)
    issue = Column(String, nullable=True)
    pages = Column(String, nullable=True)
    doi = Column(String, nullable=True)
    url = Column(String, nullable=True)
    access_date = Column(String, nullable=True)
    place = Column(String, nullable=True)
    edition = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(UTC))