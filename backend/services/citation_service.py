# backend/services/citation_service.py
from typing import Dict
from repositories.citation_repo import CitationRepository
from repositories.project_repo import ProjectRepository
from services.validators.citation_validator import validate_citation_data
from fastapi import HTTPException
import json
from services.formatters.mla_formatter import MLAFormatter
from services.formatters.apa_formatter import APAFormatter
from models.citation import Citation

class CitationService:
    """
    Service class for managing citation operations and business logic.

    This class acts as an intermediary between the API layer and the data layer,
    handling all business logic for citations including validation, duplicate detection,
    and coordination with project repositories. It ensures data integrity and provides
    formatted citation outputs in various academic styles.

    Attributes:
        _citation_repo (CitationRepository): Repository for citation database operations
        _project_repo (ProjectRepository): Repository for project database operations
    """

    def __init__(self, db):
        """
        Initialize the citation service with database repositories.

        Args:
            db (Session): SQLAlchemy database session for database operations
        """
        self._citation_repo = CitationRepository(db)
        self._project_repo = ProjectRepository(db)

    def create_citation(self, project_id: int, data: dict) -> Citation:
        """
        Create a new citation with comprehensive validation and duplicate detection.

        This method performs the following steps:
        1. Validates required parameters (project_id and data)
        2. Verifies the parent project exists
        3. Checks for duplicate citations within the project
        4. Validates citation data structure and required fields
        5. Creates and returns the citation

        Args:
            project_id (int): ID of the project to associate the citation with
            data (dict): Citation data including type, title, authors, year, etc.

        Returns:
            Citation: The newly created citation object

        Raises:
            HTTPException: 400 if parameters are invalid
            HTTPException: 404 if project doesn't exist
            HTTPException: 409 if identical citation already exists in the project
            HTTPException: 400 if validation fails

        Note:
            - All validation is performed before database operations
            - Duplicate detection uses case-insensitive comparison
        """
        # Validate required parameters
        if project_id is None:
            raise HTTPException(status_code=400, detail="project_id is required for citation creation")
        
        # Verify that the parent project exists before creating citation
        project = self._project_repo.get_by_id(project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")  
        
        if data is None:
            raise HTTPException(status_code=400, detail="data is required for citation creation")
        
        # Check if an identical citation already exists in this project
        duplicate_citation = self._citation_repo.find_duplicate_citation_in_project(project_id, data)
        if duplicate_citation:
            raise HTTPException(
                status_code=409, 
                detail="An identical citation already exists in this project"
            )
        
        # Validate the incoming citation data structure and required fields
        validate_citation_data(data, mode="create")
        
        # Create and return the new citation
        return self._citation_repo.create(project_id=project_id, **data)
    
    def get_citation(self, citation_id: int) -> Citation:
        """
        Retrieve a citation by its unique identifier.

        Args:
            citation_id (int): Unique identifier of the citation

        Returns:
            Citation: The citation object if found

        Raises:
            HTTPException: 400 if citation_id is None
            HTTPException: 404 if citation doesn't exist
        """
        # Validate required parameters
        if citation_id is None:
            raise HTTPException(status_code=400, detail="citation_id is required")
        
        citation = self._citation_repo.get_by_id(citation_id)
        if not citation:
            raise HTTPException(status_code=404, detail="Citation not found")
        return citation

    def update_citation(self, citation_id: int, project_id: int, data: dict) -> Citation:
        """
        Update an existing citation with comprehensive validation and duplicate handling.

        This method handles complex update scenarios:
        1. Validates all required parameters
        2. Verifies both project and citation exist
        3. Merges current citation data with updates
        4. Checks for duplicates after merge
        5. Detects citation type changes requiring additional validation
        6. Performs the update operation

        Args:
            citation_id (int): ID of the citation to update
            project_id (int): ID of the associated project
            data (dict): Updated citation data (partial updates allowed)

        Returns:
            Citation: The updated citation object

        Raises:
            HTTPException: 400 if required parameters are None
            HTTPException: 404 if project or citation doesn't exist
            HTTPException: 409 if update would create a duplicate in the project
            HTTPException: 400 if validation fails
            HTTPException: 500 if update operation fails

        Note:
            - If citation is shared by multiple projects, a new citation is created
            - Type changes require additional fields specific to the new type
            - Fields not valid for the citation type are set to None
        """
        # Validate required parameters
        if citation_id is None:
            raise HTTPException(status_code=400, detail="citation_id is required")
        if project_id is None:
            raise HTTPException(status_code=400, detail="project_id is required for citation updates")
        if data is None:
            raise HTTPException(status_code=400, detail="data is required for citation updates")
        
        # Verify the project exists
        project = self._project_repo.get_by_id(project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Verify the citation exists and get current state 
        # also needs to check if its in the porject
        citation = self._citation_repo.get_by_id(citation_id)
        if not citation:
            raise HTTPException(status_code=404, detail="Citation not found")
        
        # Merge current citation data with updates and filter by type
        merged_data = self._citation_repo.merge_citation_data(citation, data)
        
        # Check if the merged citation would create a duplicate in this project
        # Convert merged_data to the format expected by find_duplicate_citation_in_project
        search_data = {}
        for key, value in merged_data.items():
            if key == "authors" and isinstance(value, str):
                # Convert JSON string back to list for the search
                search_data[key] = json.loads(value) if value else []
            else:
                search_data[key] = value
        
        # Find if there's already an identical citation in this project (excluding current one)
        duplicate_citation = self._citation_repo.find_duplicate_citation_in_project(project_id, search_data)
        if duplicate_citation and duplicate_citation.id != citation_id:
            raise HTTPException(
                status_code=409,
                detail="An identical citation already exists in this project"
            )

        
        # Detect if citation type is being changed (requires special validation)
        current_type = citation.type
        new_type = data.get("type")
        type_change = new_type is not None and new_type.lower() != current_type.lower()
        
        # Validate the update data with context about type changes
        validate_citation_data(data, mode="update", current_type=current_type, type_change=type_change)
        
        # Perform the update operation
        updated = self._citation_repo.update(citation_id=citation_id, project_id=project_id, **data)
        if not updated:
            raise HTTPException(status_code=500, detail="Failed to update citation")

        return updated

    def delete_citation(self, citation_id: int, project_id: int) -> Dict[str, str]:
        """
        Delete a citation from the system or remove its association with a project.

        This method handles deletion intelligently:
        - If citation is used only by this project, deletes the citation entirely
        - If citation is shared by multiple projects, removes only the association

        Args:
            citation_id (int): ID of the citation to delete
            project_id (int): ID of the associated project

        Returns:
            dict: Success message confirming deletion

        Raises:
            HTTPException: 400 if required parameters are None
            HTTPException: 404 if project or citation doesn't exist
            HTTPException: 500 if deletion operation fails
        """
        # Validate required parameters
        if citation_id is None:
            raise HTTPException(status_code=400, detail="citation_id is required")
        if project_id is None:
            raise HTTPException(status_code=400, detail="project_id is required for citation deletion")
        
        # Verify the project exists
        project = self._project_repo.get_by_id(project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
         
        # Verify the citation exists before attempting deletion
        citation = self._citation_repo.get_by_id(citation_id)
        if not citation:
            raise HTTPException(status_code=404, detail="Citation not found")
           
        # Attempt to delete the citation
        success = self._citation_repo.delete(citation_id=citation_id, project_id=project_id)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to delete citation")
        return {"message": "Citation deleted"}

    def format_citation(self, citation: Citation, format_type: str = "apa") -> str:
        """
        Generate formatted citation string according to academic style guidelines.

        This method formats citations following official style guides (APA 7th, MLA 9th).
        Different citation types (book, article, website, report) are formatted
        according to their specific requirements in each style.

        Args:
            citation (Citation): Citation object to format
            format_type (str): Academic citation format style ("apa" or "mla")

        Returns:
            str: Formatted citation string with HTML markup for italics

        Raises:
            ValueError: If format_type is not supported (not "apa" or "mla")

        Note:
            - Formatted citations include HTML <i> tags for italics
            - APA format uses sentence case for titles
            - MLA format uses title case for titles
        """
        format_type = format_type.lower()
        
        if format_type == "apa":
            formatter = APAFormatter(citation)
            return formatter.format_citation()
        elif format_type == "mla":
            formatter = MLAFormatter(citation)
            return formatter.format_citation()
        else:
            raise ValueError(f"Unsupported format: {format_type}. Supported formats: 'apa', 'mla'")