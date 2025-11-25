# backend/services/project_service.py
from typing import Dict, List
from repositories.citation_repo import CitationRepository
from repositories.project_repo import ProjectRepository
from fastapi import HTTPException
from pydantic import ValidationError
from schemas.project_schemas import ProjectCreate, ProjectUpdate
from services.citation_service import CitationService
from models.project import Project
from models.citation import Citation

class ProjectService:
    """
    Service class for managing project operations and business logic.

    This class acts as an intermediary between the API layer and the data layer,
    handling all business logic for projects including validation, citation management,
    and bibliography generation. It coordinates between project and citation repositories
    to provide comprehensive project management features.

    Attributes:
        _db (Session): SQLAlchemy database session for database operations
        _project_repo (ProjectRepository): Repository for project database operations
        _citation_repo (CitationRepository): Repository for citation database operations
    """

    def __init__(self, db):
        """
        Initialize the project service with database repositories.

        Args:
            db (Session): SQLAlchemy database session for database operations
        """
        self._db = db
        self._project_repo = ProjectRepository(db)
        self._citation_repo = CitationRepository(db)

    def create_project(self, data: dict) -> Project:
        """
        Create a new project with validation and uniqueness checking.

        This method performs the following steps:
        1. Validates that data is provided
        2. Validates project data format and required fields
        3. Checks for duplicate project names (case-insensitive after trimming)
        4. Creates and returns the project

        Args:
            data (dict): Project data including name and other attributes

        Returns:
            Project: The newly created project object

        Raises:
            HTTPException: 400 if data is None or validation fails
            HTTPException: 409 if project name already exists

        Note:
            - Project names are trimmed and checked for uniqueness
            - Name comparison is case-sensitive after trimming
        """
        # Validate required parameters
        if data is None:
            raise HTTPException(status_code=400, detail="data is required for project creation")

        # Validate project data format using Pydantic
        try:
            validated_data = ProjectCreate(**data)
        except ValidationError as e:
            raise HTTPException(status_code=400, detail=str(e))

        # Extract name for uniqueness check (safe now after validation)
        name = validated_data.name

        # Check name uniqueness
        existing_project = self._project_repo.get_by_name(name.strip())
        if existing_project:
            raise HTTPException(
                status_code=409,
                detail=f"A project with the name '{name}' already exists"
            )

        return self._project_repo.create(validated_data.model_dump())

    def get_project(self, project_id: int) -> Project:
        """
        Retrieve a project by its unique identifier.

        Args:
            project_id (int): Unique identifier of the project

        Returns:
            Project: The project object if found

        Raises:
            HTTPException: 400 if project_id is None
            HTTPException: 404 if project doesn't exist
        """
        # Validate required parameters
        if project_id is None:
            raise HTTPException(status_code=400, detail="project_id is required")
        
        # Retrieve project and verify it exists
        project = self._project_repo.get_by_id(project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        return project

    def get_all_projects(self) -> List[Project]:
        """
        Retrieve all projects from the system.
        
        Returns:
            list: List of all project objects
        """
        return self._project_repo.get_all()

    def update_project(self, project_id: int, data: dict) -> Project:
        """
        Update an existing project with validation and uniqueness checking.

        This method validates the update data and ensures that if the name
        is being changed, it doesn't conflict with another existing project.

        Args:
            project_id (int): ID of the project to update
            data (dict): Updated project data (partial updates allowed)

        Returns:
            Project: The updated project object

        Raises:
            HTTPException: 400 if project_id or data is None
            HTTPException: 400 if validation fails
            HTTPException: 404 if project doesn't exist
            HTTPException: 409 if new name conflicts with existing project

        Note:
            - Name uniqueness check excludes the current project
            - Project names are trimmed before comparison
        """
        # Validate required parameters
        if project_id is None:
            raise HTTPException(status_code=400, detail="project_id is required")
        if data is None:
            raise HTTPException(status_code=400, detail="data is required for project updates")

        # Validate project data format using Pydantic
        try:
            validated_data = ProjectUpdate(**data)
        except ValidationError as e:
            raise HTTPException(status_code=400, detail=str(e))

        # If name is being updated, check uniqueness
        name = validated_data.name

        # Check name uniqueness (exclude current project)
        existing_project = self._project_repo.get_by_name(name.strip())
        if existing_project and existing_project.id != project_id:
            raise HTTPException(
                status_code=409,
                detail=f"A project with the name '{name}' already exists"
            )
        # Attempt to update the project
        project = self._project_repo.update(project_id, **validated_data.model_dump())
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        return project

    def delete_project(self, project_id: int) -> Dict[str, str]:
        """
        Delete a project from the system along with its citation associations.

        This method removes the project and all project-citation associations.
        Citations that are only associated with this project will also be deleted.

        Args:
            project_id (int): ID of the project to delete

        Returns:
            dict: Success message confirming deletion

        Raises:
            HTTPException: 400 if project_id is None
            HTTPException: 404 if project doesn't exist
            HTTPException: 500 if deletion operation fails

        Note:
            - Deleting a project cascades to remove project-citation associations
            - Citations used only by this project are also deleted
            - Citations shared with other projects remain in the database
        """
        # Validate required parameters
        if project_id is None:
            raise HTTPException(status_code=400, detail="project_id is required")
        
        project = self._project_repo.get_by_id(project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Attempt to delete the project
        success = self._project_repo.delete(project_id)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to delete project")
        return {"message": "Project deleted"}

    def get_all_citations_by_project(self, project_id: int) -> List[Citation]:
        """
        Retrieve all citations associated with a specific project.

        Args:
            project_id (int): ID of the project to get citations for

        Returns:
            list: List of citation objects belonging to the project

        Raises:
            HTTPException: 400 if project_id is None
            HTTPException: 404 if project doesn't exist

        Note:
            - Returns empty list if project has no citations
            - Citations are returned in database order
        """
        # Validate required parameters
        if project_id is None:
            raise HTTPException(status_code=400, detail="project_id is required")
        
        # Verify the project exists before retrieving citations
        project = self._project_repo.get_by_id(project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Return all citations for this project
        return self._project_repo.get_all_by_project(project_id)

    def generate_bibliography_by_project(self, project_id: int, format_type: str = "apa") -> Dict[str, any]:
        """
        Generate a formatted bibliography for all citations in a project.

        This method retrieves all citations for a project and formats them
        according to the specified academic style (APA or MLA). It returns
        a structured response with citation count and formatted citations.

        Args:
            project_id (int): ID of the project to generate bibliography for
            format_type (str): Citation format style ("apa" or "mla", defaults to "apa")

        Returns:
            dict: Dictionary containing:
                - project_id (int): The project identifier
                - format_type (str): The citation format used
                - bibliography (list): List of formatted citation strings
                - citation_count (int): Number of citations formatted

        Raises:
            HTTPException: 400 if project_id is None
            HTTPException: 404 if project doesn't exist
            HTTPException: 400 if unsupported format_type is provided

        Note:
            - If project has no citations, returns empty bibliography
            - Unsupported formats fall back to APA formatting
            - Citations are formatted with HTML <i> tags for italics
        """
        # Validate required parameters
        if project_id is None:
            raise HTTPException(status_code=400, detail="project_id is required")
       
        # Verify the project exists
        project = self._project_repo.get_by_id(project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
       
        # Get all citations for the project
        citations = self._project_repo.get_all_by_project(project_id)
       
        if not citations:
            return {
                "project_id": project_id,
                "format_type": format_type.lower(),
                "bibliography": [],
                "citation_count": 0
            }
       
        citation_service = CitationService(self._db)
       
        # Format each citation
        formatted_citations = []
        for citation in citations:
            try:
                formatted = citation_service.format_citation(citation, format_type)
                formatted_citations.append(formatted)
            except ValueError as e:
                # If format is not supported, default to APA
                if "Unsupported format" in str(e):
                    formatted = citation_service.format_citation(citation, "apa")
                    formatted_citations.append(formatted)
                else:
                    raise HTTPException(status_code=400, detail=str(e))
       
        return {
            "project_id": project_id,
            "format_type": format_type.lower(),
            "bibliography": formatted_citations,
            "citation_count": len(formatted_citations)
        }
