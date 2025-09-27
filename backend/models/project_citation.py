from sqlalchemy import Column, Integer, ForeignKey
from models.base import Base

class ProjectCitation(Base):
    __tablename__ = "project_citations"

    project_id = Column(Integer, ForeignKey("projects.id"), primary_key=True)
    citation_id = Column(Integer, ForeignKey("citations.id"), primary_key=True)
