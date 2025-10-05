# backend/models/__init__.py
"""
Models package for the citation generator application.

This package contains all SQLAlchemy ORM models that define the database schema:
- base.py: Base declarative class for all models
- citation.py: Citation model for bibliographic references
- project.py: Project model for organizing citations
- project_citation.py: Association table for many-to-many relationship

All models inherit from the Base class defined in base.py and are used throughout
the application for database operations via SQLAlchemy sessions.
"""
