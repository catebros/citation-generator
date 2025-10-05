# backend/services/validators/project_validator.py
from fastapi import HTTPException
from typing import Dict, List, Any, Optional
from models.project import Project
from sqlalchemy import inspect

# String length limits for validation
MAX_PROJECT_NAME_LENGTH = 200  # Generous limit for project names

def _get_project_valid_fields() -> List[str]:
    """
    Get valid fields from Project model dynamically.

    Uses SQLAlchemy inspection to extract column names from the Project model,
    excluding auto-generated fields that users should not modify.

    Returns:
        list: List of valid field names for project data

    Note:
        - Excludes 'id' (auto-generated primary key)
        - Excludes 'created_at' (auto-generated timestamp)
    """
    mapper = inspect(Project)
    excluded_fields = {'id', 'created_at'}
    return [column.key for column in mapper.columns if column.key not in excluded_fields]

PROJECT_VALID_FIELDS = _get_project_valid_fields()

def validate_project_data(data: Dict[str, Any], mode: str = "create") -> bool:
    """
    Main validation function for project data.

    This function coordinates all project validation logic including:
    - Mode-specific field requirements (create vs update)
    - Field format and content validation
    - Length limit enforcement

    Args:
        data (Dict[str, Any]): Project data to validate
        mode (str): Operation mode ("create" or "update"), defaults to "create"

    Returns:
        bool: True if validation passes

    Raises:
        HTTPException: 400 with detailed error message if validation fails

    Note:
        - Create mode requires 'name' field
        - Update mode allows partial updates
        - All provided fields must be valid for projects
    """
    _validate_fields_by_mode(data, mode)
    _validate_field_formats(data)
    
    return True

def _validate_fields_by_mode(data: Dict[str, Any], mode: str) -> None:
    """
    Route to appropriate field validation based on operation mode.

    Args:
        data (Dict[str, Any]): Project data to validate
        mode (str): Operation mode ("create" or "update")

    Note:
        - Create mode validates all required fields are present
        - Update mode allows partial updates with only field validity checks
    """
    if mode == "create":
        _validate_create_mode_fields(data)
    elif mode == "update":
        _validate_update_mode_fields(data)

def _validate_create_mode_fields(data: Dict[str, Any]) -> None:
    """
    Validate fields for create mode with strict requirements.

    For creation, all required fields must be present and no invalid
    fields should be included.

    Args:
        data (Dict[str, Any]): Project data to validate

    Raises:
        HTTPException: 400 if required 'name' field is missing or invalid fields are present

    Note:
        - 'name' is the only required field for projects
        - Rejects any fields not valid for projects
        - Valid fields are determined from Project model
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

def _validate_update_mode_fields(data: Dict[str, Any]) -> None:
    """
    Validate fields for update mode without strict requirements.

    When updating, partial updates are allowed. Only validates that
    provided fields are valid for projects.

    Args:
        data (Dict[str, Any]): Project update data (can be partial)

    Raises:
        HTTPException: 400 if any provided fields are invalid for projects

    Note:
        - Allows partial updates (not all fields required)
        - Only checks that provided fields are valid
        - Does not require 'name' field to be present
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

def _validate_field_formats(data: Dict[str, Any]) -> None:
    """
    Validate format and content of all present fields.

    This function routes each field to its specific validator.

    Args:
        data (Dict[str, Any]): Project data with fields to validate

    Raises:
        HTTPException: 400 if any field has invalid format or content

    Note:
        - Only validates fields that are present in data
        - Currently only validates 'name' field
        - Additional validators can be added to field_validators dict
    """
    field_validators = {
        "name": _validate_name,
    }

    for field, value in data.items():
        if field in field_validators:
            field_validators[field](value, field)

def _validate_name(name: Any, field_name: str) -> None:
    """
    Validate project name field format and length.

    Args:
        name (Any): Value to validate as project name
        field_name (str): Field name for error messages

    Raises:
        HTTPException: 400 if name is not a string, is empty, or exceeds length limit

    Note:
        - Must be a non-empty string
        - Whitespace-only strings are invalid
        - Maximum length is MAX_PROJECT_NAME_LENGTH (200 characters)
        - Name is trimmed before checking length
    """
    if not isinstance(name, str) or not name.strip():
        raise HTTPException(status_code=400, detail="Project name must be a non-empty string")
    
    if len(name.strip()) > MAX_PROJECT_NAME_LENGTH:
        raise HTTPException(
            status_code=400, 
            detail=f"Project name exceeds maximum length of {MAX_PROJECT_NAME_LENGTH} characters"
        )
