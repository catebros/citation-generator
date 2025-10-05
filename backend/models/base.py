# backend/models/base.py
"""
Base declarative class for SQLAlchemy ORM models.

This module defines the Base class that serves as the foundation for all database
models in the application. All model classes (Citation, Project, ProjectCitation)
inherit from this Base class to gain SQLAlchemy ORM functionality.

The declarative_base() function creates a base class that maintains a catalog of
classes and tables relative to that base, enabling SQLAlchemy to track all model
definitions and generate the corresponding database schema.
"""
from sqlalchemy.orm import declarative_base


# Base class inherited by all database models in this application
# All tables defined in models/ inherit from this to gain ORM functionality
Base = declarative_base()