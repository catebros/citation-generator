# backend/services/project_service.py
from typing import Dict, List

from fastapi import HTTPException
from models.citation import Citation
from models.project import Project
from pydantic import ValidationError
from repositories.citation_repo import CitationRepository
from repositories.project_repo import ProjectRepository
from schemas.project_schemas import ProjectCreate, ProjectUpdate
from services.citation_service import CitationService
from services.validators import ParameterValidator


class ProjectService:
    """Manage project operations and business logic with validation and citation management."""

    def __init__(self, db):
        """Initialize project service with database repositories."""
        self._db = db
        self._project_repo = ProjectRepository(db)
        self._citation_repo = CitationRepository(db)

    def create_project(self, data: dict) -> Project:
        """Create a new project with validation and uniqueness checking."""
        ParameterValidator.validate_required(data, "data")

        try:
            validated_data = ProjectCreate(**data)
        except ValidationError as e:
            raise HTTPException(status_code=400, detail=str(e))

        # Check name uniqueness
        existing_project = self._project_repo.get_by_name(validated_data.name.strip())
        ParameterValidator.validate_unique(
            bool(existing_project), validated_data.name, "Project"
        )

        return self._project_repo.create(validated_data.model_dump())

    def get_project(self, project_id: int) -> Project:
        """Retrieve a project by its unique identifier."""
        ParameterValidator.validate_required(project_id, "project_id")

        project = self._project_repo.get_by_id(project_id)
        ParameterValidator.validate_exists(project, "Project")
        return project

    def get_all_projects(self) -> List[Project]:
        """Retrieve all projects from the system."""
        return self._project_repo.get_all()

    def update_project(self, project_id: int, data: dict) -> Project:
        """Update an existing project with validation and uniqueness checking."""
        ParameterValidator.validate_required(project_id, "project_id")
        ParameterValidator.validate_required(data, "data")

        try:
            validated_data = ProjectUpdate(**data)
        except ValidationError as e:
            raise HTTPException(status_code=400, detail=str(e))

        # Check name uniqueness (exclude current project)
        existing_project = self._project_repo.get_by_name(validated_data.name.strip())
        if existing_project and existing_project.id != project_id:
            raise HTTPException(
                status_code=409,
                detail=f"A project with the name '{validated_data.name}' already exists",
            )

        project = self._project_repo.update(project_id, **validated_data.model_dump())
        ParameterValidator.validate_exists(project, "Project")
        return project

    def delete_project(self, project_id: int) -> Dict[str, str]:
        """Delete a project from the system along with its citation associations."""
        ParameterValidator.validate_required(project_id, "project_id")

        project = self._project_repo.get_by_id(project_id)
        ParameterValidator.validate_exists(project, "Project")

        success = self._project_repo.delete(project_id)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to delete project")
        return {"message": "Project deleted"}

    def get_all_citations_by_project(self, project_id: int) -> List[Citation]:
        """Retrieve all citations for a project."""
        # Validate required parameters
        if project_id is None:
            raise HTTPException(status_code=400, detail="project_id is required")

        # Verify the project exists before retrieving citations
        project = self._project_repo.get_by_id(project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")

        # Return all citations for this project
        return self._project_repo.get_all_by_project(project_id)

    def generate_bibliography_by_project(
        self, project_id: int, format_type: str = "apa"
    ) -> Dict[str, any]:
        """Generate formatted bibliography for project citations in APA or MLA style."""
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
                "citation_count": 0,
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
            "citation_count": len(formatted_citations),
        }
