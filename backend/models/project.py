# backend/models/project.py
from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime, UTC
from models.base import Base

class Project(Base):
    """
    Project model for organizing and grouping citations.
    Represents a research project or document that contains multiple citations.
    """
    __tablename__ = "projects"

    # Primary identifier
    id = Column(Integer, primary_key=True, index=True)
    
    # Project information
    name = Column(String, nullable=False)
    
    # Metadata - automatically set when project is created
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(UTC))
