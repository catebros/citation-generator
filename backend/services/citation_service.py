from repositories.citation_repo import CitationRepository
from repositories.project_repo import ProjectRepository
from services.validators.citation_validator import validate_citation_data
from fastapi import HTTPException

class CitationService:
    """
    Service class for managing citation operations.
    Handles business logic for creating, reading, updating, and deleting citations.
    """
    
    def __init__(self, db):
        """
        Initialize the citation service with database repositories.
        
        Args:
            db: Database session or connection object
        """
        self.citation_repo = CitationRepository(db)
        self.project_repo = ProjectRepository(db)

    def create_citation(self, project_id: int, data: dict):
        """
        Create a new citation with validation.
        
        Args:
            project_id (int): ID of the project to associate the citation with
            data (dict): Citation data including type, title, authors, etc.
            
        Returns:
            Citation: The newly created citation object
            
        Raises:
            HTTPException: If project doesn't exist or validation fails
        """
        # Validate required parameters
        if project_id is None:
            raise HTTPException(status_code=400, detail="project_id is required for citation creation")
        if data is None:
            raise HTTPException(status_code=400, detail="data is required for citation creation")
        
        # Verify that the parent project exists before creating citation
        project = self.project_repo.get_by_id(project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")   
        
        # Validate the incoming citation data structure and required fields
        validate_citation_data(data, mode="create")
        
        # Create and return the new citation
        return self.citation_repo.create(project_id=project_id, **data)
    
    def get_citation(self, citation_id: int):
        """
        Retrieve a citation by its unique identifier.
        
        Args:
            citation_id (int): Unique identifier of the citation
            
        Returns:
            Citation: The citation object if found
            
        Raises:
            HTTPException: If citation doesn't exist
        """
        # Validate required parameters
        if citation_id is None:
            raise HTTPException(status_code=400, detail="citation_id is required")
        
        citation = self.citation_repo.get_by_id(citation_id)
        if not citation:
            raise HTTPException(status_code=404, detail="Citation not found")
        return citation

    def update_citation(self, citation_id: int, project_id: int, data: dict):
        """
        Update an existing citation with validation.
        
        Args:
            citation_id (int): ID of the citation to update
            project_id (int): ID of the associated project
            data (dict): Updated citation data
            
        Returns:
            Citation: The updated citation object
            
        Raises:
            HTTPException: If project/citation doesn't exist or validation fails
        """
        # Validate required parameters
        if citation_id is None:
            raise HTTPException(status_code=400, detail="citation_id is required")
        if project_id is None:
            raise HTTPException(status_code=400, detail="project_id is required for citation updates")
        if data is None:
            raise HTTPException(status_code=400, detail="data is required for citation updates")
        
        # Verify the project exists
        project = self.project_repo.get_by_id(project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Verify the citation exists and get current state
        citation = self.citation_repo.get_by_id(citation_id)
        if not citation:
            raise HTTPException(status_code=404, detail="Citation not found")
        
        # Detect if citation type is being changed (requires special validation)
        current_type = citation.type
        new_type = data.get("type")
        type_change = new_type is not None and new_type.lower() != current_type.lower()
        
        # Validate the update data with context about type changes
        validate_citation_data(data, mode="update", current_type=current_type, type_change=type_change)
        
        # Perform the update operation
        updated = self.citation_repo.update(citation_id=citation_id, project_id=project_id, **data)
        if not updated:
            raise HTTPException(status_code=400, detail="Update failed")

        return updated

    def delete_citation(self, citation_id: int, project_id: int):
        """
        Delete a citation from the system.
        
        Args:
            citation_id (int): ID of the citation to delete
            project_id (int, optional): ID of the associated project
            
        Returns:
            dict: Success message confirming deletion
            
        Raises:
            HTTPException: If project/citation doesn't exist or deletion fails
        """
        # Validate required parameters
        if citation_id is None:
            raise HTTPException(status_code=400, detail="citation_id is required")
        if project_id is None:
            raise HTTPException(status_code=400, detail="project_id is required for citation deletion")
        
        # Verify the project exists
        project = self.project_repo.get_by_id(project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
         
        # Verify the citation exists before attempting deletion
        citation = self.citation_repo.get_by_id(citation_id)
        if not citation:
            raise HTTPException(status_code=404, detail="Citation not found")
           
        # Attempt to delete the citation
        success = self.citation_repo.delete(citation_id=citation_id, project_id=project_id)
        if not success:
            raise HTTPException(status_code=404, detail="Citation not found")
        return {"message": "Citation deleted"}

    def format_citation(self, citation, format_type: str = "apa") -> str:
        """
        Generate formatted citation based on citation type and format.
        
        Args:
            citation: Citation object to format
            format_type: Citation format (currently only "apa" supported)
            
        Returns:
            str: Formatted citation string
            
        Raises:
            ValueError: If format_type is not supported
        """
        format_type = format_type.lower()
        
        if format_type == "apa":
            from services.formatters.apa_formatter import APAFormatter
            formatter = APAFormatter(citation)
            return formatter.format_citation()
        elif format_type == "mla":
            from services.formatters.mla_formatter import MLAFormatter
            formatter = MLAFormatter(citation)
            return formatter.format_citation()
        else:
            raise ValueError(f"Unsupported format: {format_type}. Supported formats: 'apa', 'mla'")