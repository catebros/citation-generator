# backend/dependencies.py
"""
FastAPI dependency injection functions.
Handles database session and service dependencies.
"""

from fastapi import Depends
from sqlalchemy.orm import Session
from db.database import get_db
from services.citation_service import CitationService
from services.project_service import ProjectService

def get_citation_service(db: Session = Depends(get_db)) -> CitationService:
    """
    Dependency function to get a citation service instance.
    
    Args:
        db (Session): Database session
        
    Returns:
        CitationService: Citation service instance
    """
    return CitationService(db)

def get_project_service(db: Session = Depends(get_db)) -> ProjectService:
    """
    Dependency function to get a project service instance.
    
    Args:
        db (Session): Database session
        
    Returns:
        ProjectService: Project service instance
    """
    return ProjectService(db)