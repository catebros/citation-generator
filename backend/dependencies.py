# backend/dependencies.py
"""
FastAPI dependency injection module.

This module provides dependency injection functions for the FastAPI application.
Dependencies handle:
- Database session lifecycle management
- Service layer instantiation with proper database connections
- Request-scoped resource cleanup

These functions are used with FastAPI's Depends() to inject services
into route handlers, ensuring proper resource management and separation of concerns.
"""

from fastapi import Depends
from sqlalchemy.orm import Session
from db.database import get_db
from services.citation_service import CitationService
from services.project_service import ProjectService

def get_citation_service(db: Session = Depends(get_db)) -> CitationService:
    """
    Dependency function to provide a CitationService instance.

    Creates a new CitationService with an active database session.
    The session is automatically managed by the get_db dependency.

    Args:
        db (Session): Database session injected by FastAPI dependency system

    Returns:
        CitationService: Configured citation service instance with database access
    """
    return CitationService(db)

def get_project_service(db: Session = Depends(get_db)) -> ProjectService:
    """
    Dependency function to provide a ProjectService instance.

    Creates a new ProjectService with an active database session.
    The session is automatically managed by the get_db dependency.

    Args:
        db (Session): Database session injected by FastAPI dependency system

    Returns:
        ProjectService: Configured project service instance with database access
    """
    return ProjectService(db)