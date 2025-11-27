# backend/models/project.py
"""
Project database model for organizing citations.

This module defines the Project model which represents a container for grouping
related citations together. Projects allow users to organize citations by research
topic, paper, assignment, or any other organizational unit.

Each project can contain multiple citations through a many-to-many relationship
implemented via the ProjectCitation association table. Projects are the primary
organizational structure in the application.

Database schema constraints:
- Required fields: name
- Optional fields: None (currently minimal schema)
- Automatic timestamp: created_at (UTC timezone)

Key features:
- Projects can contain 0 or more citations
- Citations can belong to multiple projects
- Projects can generate bibliographies in APA or MLA format
- Project names are validated for length and format by project_validator
"""
from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime, timezone
from models.base import Base


class Project(Base):
    """
    SQLAlchemy ORM model for research projects.

    This model represents a project (research paper, assignment, etc.) that
    contains and organizes a collection of bibliographic citations. Projects
    serve as the primary organizational unit for citations in the application.

    Attributes:
        id (int): Primary key, auto-incremented unique identifier for the project
        name (str): Project name/title (required, validated by project_validator)
        created_at (datetime): Timestamp when project was created (UTC, auto-set)

    Relationships:
        - Many-to-many with Citation through ProjectCitation association table
        - A project can contain multiple citations
        - When a project is deleted, all its citation associations are removed (CASCADE)

    Table name: projects

    Indexes:
        - Primary key index on id column for fast lookups

    Notes:
        - Project names have max length limit (MAX_PROJECT_NAME_LENGTH in validator)
        - Empty or whitespace-only names are rejected by validation
        - Projects can generate formatted bibliographies via project_service
        - Citations are added to projects through citation_service.create_citation()
    """
    __tablename__ = "projects"

    # ========== PRIMARY KEY ==========
    # Unique identifier for each project, auto-incremented by database
    id = Column(Integer, primary_key=True, index=True, autoincrement="auto")

    # ========== REQUIRED FIELDS ==========
    # Project identification and description
    name = Column(String, nullable=False)  # Project name/title

    # ========== METADATA ==========
    # Automatically managed timestamp fields
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))  # Creation timestamp (UTC)
