# backend/repositories/project_repo.py
"""
Project repository for CRUD operations with orphan citation cleanup.
"""
from typing import Any, Dict, List, Optional

from models.citation import Citation
from models.project import Project
from models.project_citation import ProjectCitation
from sqlalchemy.orm import Session


class ProjectRepository:
    """Handle project CRUD and manage citations with automatic orphan cleanup."""

    def __init__(self, db: Session) -> None:
        """Initialize repository with database session."""
        self._db = db

    def create(self, data: Dict[str, Any]) -> Project:
        """Create new project with provided data."""
        project = Project(name=data["name"])
        self._db.add(project)
        self._db.commit()
        self._db.refresh(project)
        return project

    def get_by_id(self, project_id: int) -> Optional[Project]:
        """Retrieve project by identifier."""
        return self._db.query(Project).filter(Project.id == project_id).first()

    def get_all(self) -> List[Project]:
        """Retrieve all projects ordered by creation date (newest first)."""
        return self._db.query(Project).order_by(Project.created_at.desc()).all()

    def update(self, project_id: int, **kwargs) -> Optional[Project]:
        """Update project attributes and return updated instance."""
        project = self.get_by_id(project_id)

        if not project:
            return None

        # Update only non-None values and existing attributes
        for key, value in kwargs.items():
            if value is None:
                continue

            if hasattr(project, key):
                setattr(project, key, value)

        self._db.commit()
        self._db.refresh(project)
        return project

    def get_all_by_project(self, project_id: int) -> List[Citation]:
        """Retrieve all citations for a project ordered by creation date."""
        return (
            self._db.query(Citation)
            .join(ProjectCitation, Citation.id == ProjectCitation.citation_id)
            .filter(ProjectCitation.project_id == project_id)
            .order_by(Citation.created_at.desc())
            .all()
        )

    def delete(self, project_id: int) -> bool:
        """Delete project and handle orphaned citations automatically."""
        project = self.get_by_id(project_id)
        if not project:
            return False

        # Get citations associated with this project
        citations_to_check = (
            self._db.query(Citation.id)
            .join(ProjectCitation, Citation.id == ProjectCitation.citation_id)
            .filter(ProjectCitation.project_id == project_id)
            .all()
        )

        # Delete ProjectCitation associations for this project
        self._db.query(ProjectCitation).filter(
            ProjectCitation.project_id == project_id
        ).delete(synchronize_session=False)

        # Check for orphaned citations and delete them
        for (citation_id,) in citations_to_check:
            remaining_assocs = (
                self._db.query(ProjectCitation)
                .filter(ProjectCitation.citation_id == citation_id)
                .count()
            )

            if remaining_assocs == 0:
                self._db.query(Citation).filter(Citation.id == citation_id).delete(
                    synchronize_session=False
                )

        # Finally delete the project
        self._db.delete(project)
        self._db.commit()
        return True

    def get_by_name(self, name: str) -> Optional[Project]:
        """Retrieve project by name using case-insensitive search."""
        return self._db.query(Project).filter(Project.name.ilike(name)).first()
