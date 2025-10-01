# backend/models/project_citation.py
from sqlalchemy import Column, Integer, ForeignKey
from models.base import Base

class ProjectCitation(Base):
    """
    Association table for many-to-many relationship between Projects and Citations.
    This model represents the junction table that links projects with their citations.
    """
    __tablename__ = "project_citations"

    # Foreign key to projects table - when a project is deleted, all its citations are removed (CASCADE)
    project_id = Column(Integer, ForeignKey("projects.id"), primary_key=True)
    
    # Foreign key to citations table - part of composite primary key
    citation_id = Column(Integer, ForeignKey("citations.id"), primary_key=True)
