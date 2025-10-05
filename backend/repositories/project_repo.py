# backend/repositories/project_repo.py
"""
Project repository for database operations.

This module provides the ProjectRepository class which handles all database
interactions for Project entities. It implements the repository pattern to
separate data access logic from business logic.

Key features:
- CRUD operations for projects
- Citation retrieval for projects (via many-to-many relationship)
- Orphan citation cleanup when deleting projects
- Case-insensitive project name search

The repository ensures data integrity by:
- Automatically removing orphaned citations when deleting projects
- Preserving shared citations that belong to other projects
- Managing ProjectCitation associations transparently
- Ordering results by creation date for predictable behavior
"""
from sqlalchemy.orm import Session
from models.project import Project
from models.citation import Citation
from models.project_citation import ProjectCitation
from typing import List, Dict, Any


class ProjectRepository:
    """
    Repository class for managing Project entities and their operations.

    This class handles all database interactions for projects including CRUD
    operations and retrieval of associated citations. It manages the many-to-many
    relationship with citations through the ProjectCitation association table.

    The repository implements intelligent deletion:
    - When deleting a project, first identifies all its citations
    - Removes all ProjectCitation associations for the project
    - Checks each citation to see if it's now orphaned (no other projects use it)
    - Deletes orphaned citations automatically to keep database clean
    - Preserves citations that are still used by other projects

    Attributes:
        _db (Session): SQLAlchemy database session for executing queries
    """

    def __init__(self, db: Session) -> None:
        """
        Initialize the repository with a database session.

        Args:
            db (Session): SQLAlchemy database session
        """
        self._db = db

    def create(self, data: Dict[str, Any]) -> Project:
        """
        Create a new project with the given data.
        
        Args:
            data (dict): The project data containing name and other attributes
            
        Returns:
            Project: The newly created project instance
        """
        project = Project(name=data["name"])
        self._db.add(project)
        self._db.commit()
        self._db.refresh(project)
        return project
    
    def get_by_id(self, project_id: int) -> Project | None:
        """
        Retrieve a project by its ID.
        
        Args:
            project_id (int): The ID of the project to retrieve
            
        Returns:
            Project | None: The project if found, None otherwise
        """
        return self._db.query(Project).filter(Project.id == project_id).first()
    
    def get_all(self) -> List[Project]:
        """
        Retrieve all projects from the database.
        
        Returns:
            list[Project]: List of all projects ordered by creation date (newest first)
        """
        return self._db.query(Project).order_by(Project.created_at.desc()).all()
    
    def update(self, project_id: int, **kwargs) -> Project | None:
        """
        Update a project with the provided key-value pairs.
        
        Args:
            project_id (int): The ID of the project to update
            **kwargs: Key-value pairs of attributes to update
            
        Returns:
            Project | None: The updated project if found, None otherwise
        """
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
        """
        Retrieve all citations associated with a specific project.
        Citations are ordered by year in descending order.
        
        Args:
            project_id (int): The ID of the project
            
        Returns:
            list[Citation]: List of citations associated with the project
        """
        return (
            self._db.query(Citation)
            .join(ProjectCitation, Citation.id == ProjectCitation.citation_id)
            .filter(ProjectCitation.project_id == project_id)
            .order_by(Citation.created_at.desc())
            .all()
        )      

    def delete(self, project_id: int) -> bool:
        """
        Delete a project and handle orphaned citations.
        First deletes ProjectCitation associations, then removes orphaned citations.
        """
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
        self._db.query(ProjectCitation).filter(ProjectCitation.project_id == project_id).delete(synchronize_session=False)

        # Check for orphaned citations and delete them
        for (citation_id,) in citations_to_check:
            remaining_assocs = (
                self._db.query(ProjectCitation)
                .filter(ProjectCitation.citation_id == citation_id)
                .count()
            )
            
            if remaining_assocs == 0:
                self._db.query(Citation).filter(
                    Citation.id == citation_id
                ).delete(synchronize_session=False)

        # Finally delete the project
        self._db.delete(project)
        self._db.commit()
        return True

    def get_by_name(self, name: str) -> Project | None:
        """
        Retrieve a project by its name (case-insensitive).

        Args:
            name (str): The name of the project to retrieve

        Returns:
            Project | None: The project if found, None otherwise
        """
        return self._db.query(Project).filter(Project.name.ilike(name)).first()