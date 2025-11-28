# backend/models/citation.py
"""
Citation database model for bibliographic references.

This module defines the Citation model which represents a single bibliographic citation
in the database. Citations can be of various types (book, article, website, report)
and contain different fields depending on their type.

The model supports:
- Book citations: type, title, authors, year, publisher, edition, place
- Article citations: type, title, authors, year, journal, volume, issue, pages, doi
- Website citations: type, title, authors, year, publisher, url, access_date
- Report citations: type, title, authors, year, publisher, url, place

Authors are stored as JSON-serialized lists in the Text field, allowing for
multiple authors per citation. Citations are linked to projects through the
ProjectCitation association table.

Database schema constraints:
- Required fields: type, title, authors
- Optional fields: All publication details, validated by citation_validator
- Automatic timestamp: created_at (UTC timezone)
"""
from datetime import datetime, timezone

from models.base import Base
from sqlalchemy import Column, DateTime, Integer, String, Text


class Citation(Base):
    """
    SQLAlchemy ORM model for bibliographic citations.

    This model stores bibliographic reference information with support for multiple
    citation types (book, article, website, report). Each citation type requires
    different fields, which are validated by the citation_validator module before
    database insertion.

    Attributes:
        id (int): Primary key, auto-incremented unique identifier for the citation
        type (str): Citation type - must be 'book', 'article', 'website', or 'report'
        title (str): Title of the work being cited (required for all types)
        authors (str): JSON-serialized list of author names (required for all types)
        year (int): Publication year (optional, can be None for undated works)

        publisher (str): Publisher name (required for books, websites, reports)
        journal (str): Journal name (required for articles, optional otherwise)
        volume (int): Volume number (used for articles and multi-volume books)
        issue (str): Issue number (used for journal articles)
        pages (str): Page range (e.g., "123-145" for articles)
        doi (str): Digital Object Identifier (used for articles)
        url (str): Web URL (required for websites, optional for others)
        access_date (str): Date accessed in YYYY-MM-DD format (used for websites)
        place (str): Place of publication (used for books and reports)
        edition (int): Edition number (used for books, 1st edition typically omitted)

        created_at (datetime): Timestamp when citation was created (UTC, auto-set)

    Relationships:
        - Many-to-many with Project through ProjectCitation association table
        - A citation can belong to multiple projects
        - A project can contain multiple citations

    Table name: citations

    Indexes:
        - Primary key index on id column for fast lookups

    Notes:
        - Authors field stores JSON array: '["John Smith", "Jane Doe"]'
        - Type-specific field requirements enforced by citation_validator
        - Formatted by APAFormatter or MLAFormatter for display
    """

    __tablename__ = "citations"

    # ========== PRIMARY KEY ==========
    # Unique identifier for each citation, auto-incremented by database
    id = Column(Integer, primary_key=True, index=True, autoincrement="auto")

    # ========== REQUIRED FIELDS ==========
    # These fields are required for all citation types
    type = Column(
        String, nullable=False
    )  # Citation type: 'book', 'article', 'website', 'report'
    title = Column(String, nullable=False)  # Title of the cited work
    authors = Column(Text, nullable=False)  # JSON array of author names stored as text
    year = Column(Integer, nullable=True)  # Publication year (None for undated works)

    # ========== PUBLICATION DETAILS ==========
    # Optional fields used by different citation types
    # Field usage varies by type - see CitationFieldsConfig in citation_validator.py
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

    # ========== METADATA ==========
    # Automatically managed timestamp fields
    created_at = Column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )  # Creation timestamp (UTC)
