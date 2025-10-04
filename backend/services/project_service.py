# backend/services/project_service.py
from repositories.citation_repo import CitationRepository
from repositories.project_repo import ProjectRepository
from fastapi import HTTPException
from services.validators.project_validator import validate_project_data

class ProjectService:
    """
    Service class for managing project operations.
    Handles business logic for creating, reading, updating, and deleting projects.
    """
    
    def __init__(self, db):
        """
        Initialize the project service with database repositories.
        
        Args:
            db: Database session or connection object
        """
        self._db = db
        self._project_repo = ProjectRepository(db)
        self._citation_repo = CitationRepository(db)

    def create_project(self, data: dict):
        """
        Create a new project with validation.
        
        Args:
            data (dict): Project data including name and other attributes
            
        Returns:
            Project: The newly created project object
            
        Raises:
            HTTPException: If data is missing or project name already exists
        """
        # Validate required parameters
        if data is None:
            raise HTTPException(status_code=400, detail="data is required for project creation")
        
        # Validate project data format (includes name validation)
        validate_project_data(data, mode="create")
        
        # Extract name for uniqueness check (safe now after validation)
        name = data.get("name")
        
        # Check name uniqueness
        existing_project = self._project_repo.get_by_name(name.strip())
        if existing_project:
            raise HTTPException(
                status_code=409, 
                detail=f"A project with the name '{name}' already exists"
            )

        return self._project_repo.create(data)

    def get_project(self, project_id: int):
        """
        Retrieve a project by its unique identifier.
        
        Args:
            project_id (int): Unique identifier of the project
            
        Returns:
            Project: The project object if found
            
        Raises:
            HTTPException: If project_id is None or project doesn't exist
        """
        # Validate required parameters
        if project_id is None:
            raise HTTPException(status_code=400, detail="project_id is required")
        
        # Retrieve project and verify it exists
        project = self._project_repo.get_by_id(project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        return project

    def get_all_projects(self):
        """
        Retrieve all projects from the system.
        
        Returns:
            list: List of all project objects
        """
        return self._project_repo.get_all()

    def update_project(self, project_id: int, data: dict):
        """
        Update an existing project with validation.
        
        Args:
            project_id (int): ID of the project to update
            data (dict): Updated project data
            
        Returns:
            Project: The updated project object
            
        Raises:
            HTTPException: If project_id/data is None or project doesn't exist
        """
        # Validate required parameters
        if project_id is None:
            raise HTTPException(status_code=400, detail="project_id is required")
        if data is None:
            raise HTTPException(status_code=400, detail="data is required for project updates")
        
        # Validate project data format (includes name validation)
        validate_project_data(data, mode="update")
        
        # If name is being updated, check uniqueness
        name = data["name"]
            
            # Check name uniqueness (exclude current project)
        existing_project = self._project_repo.get_by_name(name.strip())
        if existing_project and existing_project.id != project_id:
            raise HTTPException(
                status_code=409, 
                detail=f"A project with the name '{name}' already exists"
            )        # Attempt to update the project
        project = self._project_repo.update(project_id, **data)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        return project

    def delete_project(self, project_id: int):
        """
        Delete a project from the system.
        
        Args:
            project_id (int): ID of the project to delete
            
        Returns:
            dict: Success message confirming deletion
            
        Raises:
            HTTPException: If project_id is None or project doesn't exist
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

    def get_all_citations_by_project(self, project_id: int):
        """
        Retrieve all citations associated with a specific project.
        
        Args:
            project_id (int): ID of the project to get citations for
            
        Returns:
            list: List of citation objects belonging to the project
            
        Raises:
            HTTPException: If project_id is None or project doesn't exist
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

    def generate_bibliography_by_project(self, project_id: int, format_type: str = "apa"):
        """
        Generate a formatted bibliography for a specific project.
       
        Args:
            project_id (int): ID of the project to generate bibliography for
            format_type (str): Citation format (apa, mla)
           
        Returns:
            dict: Dictionary with bibliography data including formatted citations
           
        Raises:
            HTTPException: If project_id is None or project doesn't exist
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
       
        # Import citation service to format citations
        from services.citation_service import CitationService
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
