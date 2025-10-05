# backend/services/validators/project_validator.py
from fastapi import HTTPException
from typing import Dict, List, Any, Optional
from models.project import Project
from sqlalchemy import inspect

# String length limits for validation
MAX_PROJECT_NAME_LENGTH = 200  # Generous limit for project names

def _get_project_valid_fields():
    """Get valid fields from Project model, excluding id and created_at."""
    mapper = inspect(Project)
    excluded_fields = {'id', 'created_at'}
    return [column.key for column in mapper.columns if column.key not in excluded_fields]

PROJECT_VALID_FIELDS = _get_project_valid_fields()

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
    _validate_fields_by_mode(data, mode)
    _validate_field_formats(data)
    
    return True

def _validate_fields_by_mode(data: Dict[str, Any], mode: str):
    """Validate fields based on operation mode."""
    if mode == "create":
        _validate_create_mode_fields(data)
    elif mode == "update":
        _validate_update_mode_fields(data)

def _validate_create_mode_fields(data: Dict[str, Any]):
    """
    Validate fields for create mode - all required fields must be present and only 
    valid fields are allowed.
    """
    # Check for missing required fields (name is required for projects)
    required_fields = ["name"]
    missing = [field for field in required_fields if field not in data]
    if missing:
        raise HTTPException(
            status_code=400,
            detail=f"Missing required project fields: {', '.join(missing)}"
        )
    
    # Check for invalid fields (fields not allowed for projects)
    provided_fields = set(data.keys())
    valid_fields = set(PROJECT_VALID_FIELDS)
    invalid_fields = provided_fields - valid_fields
    
    if invalid_fields:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid fields for project: {', '.join(invalid_fields)}. "
                   f"Valid fields: {', '.join(sorted(valid_fields))}"
        )

def _validate_update_mode_fields(data: Dict[str, Any]):
    """
    Validate fields for update mode - all provided fields must be valid for projects.
    """
    # Check for invalid fields (fields not allowed for projects)
    provided_fields = set(data.keys())
    valid_fields = set(PROJECT_VALID_FIELDS)
    invalid_fields = provided_fields - valid_fields
    
    if invalid_fields:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid fields for project: {', '.join(invalid_fields)}. "
                   f"Valid fields: {', '.join(sorted(valid_fields))}"
        )

def _validate_field_formats(data: Dict[str, Any]):
    """Validate format of all present fields."""
    field_validators = {
        "name": _validate_name,
    }
    
    for field, value in data.items():
        if field in field_validators:
            field_validators[field](value, field)

def _validate_name(name: Any, field_name: str):
    """Validate name field - must be a non-empty string with reasonable length."""
    if not isinstance(name, str) or not name.strip():
        raise HTTPException(status_code=400, detail="Project name must be a non-empty string")
    
    if len(name.strip()) > MAX_PROJECT_NAME_LENGTH:
        raise HTTPException(
            status_code=400, 
            detail=f"Project name exceeds maximum length of {MAX_PROJECT_NAME_LENGTH} characters"
        )
