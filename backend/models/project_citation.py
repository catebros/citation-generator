# backend/models/project_citation.py
from models.base import Base
from sqlalchemy import Column, ForeignKey, Integer


class ProjectCitation(Base):
    __tablename__ = "project_citations"

    # Foreign key to projects table - when a project is deleted, all its citation associations are removed (CASCADE)
    project_id = Column(Integer, ForeignKey("projects.id"), primary_key=True)

    # Foreign key to citations table
    citation_id = Column(Integer, ForeignKey("citations.id"), primary_key=True)
