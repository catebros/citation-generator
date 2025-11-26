# backend/services/validators/validators.py
"""Reusable parameter validation logic following DRY and SRP principles."""

from fastapi import HTTPException


class ParameterValidator:
    """Centralized parameter validation methods for services."""
    
    @staticmethod
    def validate_required(value, field_name: str, status_code: int = 400) -> None:
        """Validate that required parameter is not None or empty."""
        if value is None or (isinstance(value, str) and value.strip() == ""):
            raise HTTPException(
                status_code=status_code,
                detail=f"{field_name} is required"
            )
    
    @staticmethod
    def validate_exists(obj, obj_type: str, status_code: int = 404) -> None:
        """Validate that resource exists in database."""
        if not obj:
            raise HTTPException(
                status_code=status_code,
                detail=f"{obj_type} not found"
            )
    
    @staticmethod
    def validate_unique(exists: bool, name: str, obj_type: str, status_code: int = 409) -> None:
        """Validate that named resource is unique."""
        if exists:
            raise HTTPException(
                status_code=status_code,
                detail=f"A {obj_type.lower()} with name '{name}' already exists"
            )
    
    @staticmethod
    def validate_not_duplicate(is_valid: bool, condition: str, status_code: int = 409) -> None:
        """Validate that resource is not a duplicate."""
        if not is_valid:
            raise HTTPException(
                status_code=status_code,
                detail=f"An {condition}"
            )
