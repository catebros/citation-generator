# backend/models/project_citation.py
"""
Association table for many-to-many relationship between Projects and Citations.

This module defines the ProjectCitation model, which implements a junction table
for the many-to-many relationship between projects and citations. This allows:
- One project to contain multiple citations
- One citation to belong to multiple projects

The relationship is managed through composite primary keys (project_id, citation_id)
which ensures that each project-citation pairing is unique in the database.

Database schema:
- Composite primary key: (project_id, citation_id)
- Foreign keys with referential integrity constraints
- No additional metadata or timestamp fields (pure association table)

Cascade behavior:
- When a project is deleted, all its associations are removed automatically
- Citations themselves are NOT deleted when removed from a project
- This is a pure linking table with no independent data
"""
from models.base import Base
from sqlalchemy import Column, ForeignKey, Integer


class ProjectCitation(Base):
    """
    SQLAlchemy ORM model for project-citation associations.

    This is a pure association table (junction table) that implements the
    many-to-many relationship between Project and Citation models. Each row
    represents a single citation belonging to a single project.

    Attributes:
        project_id (int): Foreign key to projects.id (part of composite primary key)
        citation_id (int): Foreign key to citations.id (part of composite primary key)

    Primary Key:
        - Composite primary key on (project_id, citation_id)
        - Ensures each citation can only be added to a project once
        - Prevents duplicate project-citation associations

    Foreign Keys:
        project_id -> projects.id:
            - Links to the Project that contains the citation
            - When project is deleted, associations are removed (CASCADE)

        citation_id -> citations.id:
            - Links to the Citation being added to the project
            - Citation record remains even if removed from all projects

    Table name: project_citations

    Relationships:
        - Many ProjectCitations -> One Project
        - Many ProjectCitations -> One Citation
        - Enables many-to-many between Projects and Citations

    Notes:
        - No independent id column (uses composite key)
        - No created_at timestamp (associations are ephemeral)
        - Managed through project_service and citation_service operations
        - Queried to get all citations in a project or all projects containing a citation
    """

    __tablename__ = "project_citations"

    # ========== COMPOSITE PRIMARY KEY & FOREIGN KEYS ==========
    # Foreign key to projects table - when a project is deleted, all its citation associations are removed (CASCADE)
    project_id = Column(Integer, ForeignKey("projects.id"), primary_key=True)

    # Foreign key to citations table - part of composite primary key
    # Citations remain in database even if removed from all projects
    citation_id = Column(Integer, ForeignKey("citations.id"), primary_key=True)
