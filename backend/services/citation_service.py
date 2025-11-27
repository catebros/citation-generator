# backend/services/citation_service.py
from typing import Dict
import json
from repositories.citation_repo import CitationRepository
from repositories.project_repo import ProjectRepository
from schemas.citation_schemas import CitationCreate, CitationUpdate
from fastapi import HTTPException
from pydantic import ValidationError
from services.formatters.mla_formatter import MLAFormatter
from services.formatters.apa_formatter import APAFormatter
from models.citation import Citation
from services.validators import ParameterValidator, CitationTypeValidator, SUPPORTED_FORMATS

class CitationService:
    """Manage citation operations with validation, duplicate detection, and formatting."""

    def __init__(self, db):
        """Initialize citation service with database repositories."""
        self._citation_repo = CitationRepository(db)
        self._project_repo = ProjectRepository(db)

    def create_citation(self, project_id: int, data: dict) -> Citation:
        """Create new citation with validation, duplicate detection, and database persistence."""
        # Validate required parameters
        if project_id is None:
            raise HTTPException(status_code=400, detail="project_id is required for citation creation")
        
        # Verify that the parent project exists before creating citation
        project = self._project_repo.get_by_id(project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")  
        
        if data is None:
            raise HTTPException(status_code=400, detail="data is required for citation creation")
        
        # Validate the incoming citation data structure and required fields using Pydantic FIRST
        try:
            validated_data = CitationCreate(**data)
        except ValidationError as e:
            raise HTTPException(status_code=400, detail=str(e))

        # Now check if an identical citation already exists in this project (with validated data)
        duplicate_citation = self._citation_repo.find_duplicate_citation_in_project(project_id, data)
        if duplicate_citation:
            raise HTTPException(
                status_code=409,
                detail="An identical citation already exists in this project"
            )

        # Get dictionary for database - no extra conversions needed
        citation_dict = validated_data.model_dump()

        # Create and return the new citation
        return self._citation_repo.create(project_id=project_id, **citation_dict)
    
    def get_citation(self, citation_id: int) -> Citation:
        """Retrieve a citation by its ID."""
        # Validate required parameters
        if citation_id is None:
            raise HTTPException(status_code=400, detail="citation_id is required")
        
        citation = self._citation_repo.get_by_id(citation_id)
        if not citation:
            raise HTTPException(status_code=404, detail="Citation not found")
        return citation

    def update_citation(self, citation_id: int, project_id: int, data: dict) -> Citation:
        """Update citation with validation, duplicate detection, and type-change handling."""
        ParameterValidator.validate_required(citation_id, "citation_id")
        ParameterValidator.validate_required(project_id, "project_id")
        ParameterValidator.validate_required(data, "data")
        
        project = self._project_repo.get_by_id(project_id)
        ParameterValidator.validate_exists(project, "Project")
        
        citation = self._citation_repo.get_by_id(citation_id)
        ParameterValidator.validate_exists(citation, "Citation")
        
        # Merge current citation data with updates
        merged_data = self._citation_repo.merge_citation_data(citation, data)
        
        # Check for duplicates (excluding current citation)
        duplicate_citation = self._citation_repo.find_duplicate_citation_in_project(project_id, merged_data)
        if duplicate_citation and duplicate_citation.id != citation_id:
            raise HTTPException(
                status_code=409,
                detail="An identical citation already exists in this project"
            )
        
        # Detect if citation type is being changed
        current_type = citation.type
        new_type = data.get("type")
        type_change = new_type is not None and new_type.lower() != current_type.lower()
        
        # Validate the update data
        try:
            validated_data = CitationUpdate(**data)
        except ValidationError as e:
            raise HTTPException(status_code=400, detail=str(e))
        
        # Get validated data and check type change if applicable
        citation_dict = validated_data.model_dump(exclude_none=True)
        
        if type_change:
            CitationTypeValidator.validate_type_change(citation_dict, new_type, current_type)
        
        # Perform the update
        updated = self._citation_repo.update(citation_id=citation_id, project_id=project_id, **citation_dict)
        if not updated:
            raise HTTPException(status_code=500, detail="Failed to update citation")
        
        return updated


    def delete_citation(self, citation_id: int, project_id: int) -> Dict[str, str]:
        """Delete citation from the system and remove project associations."""
        ParameterValidator.validate_required(citation_id, "citation_id")
        ParameterValidator.validate_required(project_id, "project_id")
        
        project = self._project_repo.get_by_id(project_id)
        ParameterValidator.validate_exists(project, "Project")
        
        citation = self._citation_repo.get_by_id(citation_id)
        ParameterValidator.validate_exists(citation, "Citation")
        
        success = self._citation_repo.delete(citation_id=citation_id, project_id=project_id)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to delete citation")
        return {"message": "Citation deleted"}

    def format_citation(self, citation: Citation, format_type: str = "apa") -> str:
        """Format citation in APA or MLA style."""
        format_type = format_type.lower()
        
        formatters = {
            "apa": APAFormatter,
            "mla": MLAFormatter
        }
        
        formatter_class = formatters.get(format_type)
        if not formatter_class:
            raise ValueError(f"Unsupported format: {format_type}. Supported formats: {', '.join(formatters.keys())}")
        
        formatter = formatter_class(citation)
        return formatter.format_citation()