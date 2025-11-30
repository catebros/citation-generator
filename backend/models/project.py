# backend/models/project.py
from datetime import datetime, timezone

from models.base import Base
from sqlalchemy import Column, DateTime, Integer, String


class Project(Base):
    __tablename__ = "projects"

    # PRIMARY KEY
    # Unique identifier for each project, auto-incremented by database
    id = Column(Integer, primary_key=True, index=True, autoincrement="auto")

    name = Column(String, nullable=False)  # Project name/title
    
    # Automatically managed timestamp fields
    created_at = Column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )  # Creation timestamp (UTC)
