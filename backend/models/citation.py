# backend/models/citation.py
from sqlalchemy import Column, Integer, String, Text, DateTime
from datetime import datetime, UTC
from models.base import Base

class Citation(Base):
    """
    Citation model for storing bibliographic references.
    Supports various citation types like books, journal articles, websites, and reports.
    """
    __tablename__ = "citations"

    # Primary identifier
    id = Column(Integer, primary_key=True, index=True)
    
    # Basic citation information
    type = Column(String, nullable=False)  
    title = Column(String, nullable=False)
    authors = Column(Text, nullable=False)  
    year = Column(Integer, nullable=True)
    
    # Publication details (optional fields for different citation types)
    publisher = Column(String, nullable=True)
    journal = Column(String, nullable=True)
    volume = Column(Integer, nullable=True)
    issue = Column(String, nullable=True)
    pages = Column(String, nullable=True)
    doi = Column(String, nullable=True)
    url = Column(String, nullable=True)
    access_date = Column(String, nullable=True)
    place = Column(String, nullable=True)
    edition = Column(Integer, nullable=True)
    
    # Metadata - automatically set when citation is created
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(UTC))
