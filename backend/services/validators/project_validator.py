from fastapi import HTTPException
from typing import Dict, Any, Optional

def validate_project_data(data: Dict[str, Any], mode: str = "create"):
    """
    Main validation function for project data.
    
    Args:
        data: Project data to validate
        mode: Operation mode ("create" or "update")
    
    Returns:
        True if validation passes
        
    Raises:
        HTTPException: If validation fails
    """
    _validate_field_formats(data)
    
    return True

def _validate_field_formats(data: Dict[str, Any]):
    """Validate format of all present fields."""
    field_validators = {
        "name": _validate_name,
    }
    
    for field, value in data.items():
        if field in field_validators and value:
            field_validators[field](value, field)

def _validate_name(name: Any, field_name: str):
    """Validate name field - must be a non-empty string."""
    if not isinstance(name, str) or not name.strip():
        raise HTTPException(status_code=400, detail="Project name must be a non-empty string")

def validate_unique_name(name: str, project_repo, exclude_id: Optional[int] = None):
    """
    Validate that project name is unique.
    
    Args:
        name: Project name to validate
        project_repo: Project repository instance
        exclude_id: Project ID to exclude from uniqueness check (for updates)
    
    Returns:
        True if name is unique
        
    Raises:
        HTTPException: If name already exists
    """
    existing_project = project_repo.get_by_name(name.strip())
    
    if existing_project and (exclude_id is None or existing_project.id != exclude_id):
        raise HTTPException(
            status_code=400, 
            detail="Project with this name already exists"
        )
    
    return True
