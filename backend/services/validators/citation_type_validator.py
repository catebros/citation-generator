# backend/services/validators/citation_type_validator.py
"""Citation type validation logic following SRP."""

from fastapi import HTTPException
from services.validators.constants import CITATION_TYPES_CONFIG


class CitationTypeValidator:
    """Handles validation of citation type changes and field requirements."""

    @staticmethod
    def validate_type_change(data: dict, new_type: str, current_type: str) -> None:
        """Validate fields when changing citation type, checking required and valid fields."""
        new_type_lower = new_type.lower()
        current_type_lower = current_type.lower()

        # Check for invalid fields
        valid_fields = CitationTypeValidator.get_valid_fields(new_type_lower)
        provided_fields = set(data.keys())
        invalid_fields = provided_fields - valid_fields

        if invalid_fields:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid fields for new type {new_type}: {', '.join(invalid_fields)}. "
                f"Valid fields: {', '.join(sorted(valid_fields))}",
            )

        # Check for missing required fields
        new_required = CitationTypeValidator.get_required_fields(new_type_lower)
        current_required = CitationTypeValidator.get_required_fields(current_type_lower)
        additional_required = new_required - current_required

        missing = [
            field
            for field in additional_required
            if field not in data and field != "type"
        ]

        if missing:
            raise HTTPException(
                status_code=400,
                detail=f"When changing to type '{new_type}', the following fields are required: {', '.join(missing)}",
            )

    @staticmethod
    def get_required_fields(citation_type: str) -> set:
        """Get required fields for a citation type from configuration."""
        config = CITATION_TYPES_CONFIG.get(citation_type.lower(), {})
        return set(config.get("required", []))

    @staticmethod
    def get_valid_fields(citation_type: str) -> set:
        """Get all valid fields for a citation type from configuration."""
        config = CITATION_TYPES_CONFIG.get(citation_type.lower(), {})
        return set(config.get("valid", []))
