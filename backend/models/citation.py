# backend/models/citation.py
from datetime import datetime, timezone

from models.base import Base
from sqlalchemy import Column, DateTime, Integer, String, Text


class Citation(Base):
    __tablename__ = "citations"

    # PRIMARY KEY
    id = Column(Integer, primary_key=True, index=True, autoincrement="auto")

    # REQUIRED FIELDS
    # These fields are required for all citation types
    type = Column(
        String, nullable=False
    )  # Citation type: 'book', 'article', 'website', 'report'
    title = Column(String, nullable=False)  # Title of the cited work
    authors = Column(Text, nullable=False)  # JSON array of author names stored as text
    year = Column(Integer, nullable=True)  # Publication year (None for undated works)


    # Optional fields used by different citation types
    publisher = Column(String, nullable=True)  # Publisher/Institution/Website name
    journal = Column(String, nullable=True)  # Journal name (for articles)
    volume = Column(Integer, nullable=True)  # Volume number
    issue = Column(
        String, nullable=True
    )  # Issue number (stored as string to support formats like "3-4")
    pages = Column(String, nullable=True)  # Page range (e.g., "123-145")
    doi = Column(String, nullable=True)  # Digital Object Identifier (for articles)
    url = Column(String, nullable=True)  # Web URL (for websites and online resources)
    access_date = Column(String, nullable=True)  # Access date in YYYY-MM-DD format
    place = Column(String, nullable=True)  # Place of publication (for books/reports)
    edition = Column(Integer, nullable=True)  # Edition number (1, 2, 3, etc.)

    # Automatically managed timestamp fields
    created_at = Column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )  
