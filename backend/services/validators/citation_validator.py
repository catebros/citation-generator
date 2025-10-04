# backend/services/validators/citation_validator.py
from fastapi import HTTPException
import re
from datetime import datetime
from typing import Dict, List, Any, Optional
from config.citation_config import CitationFieldsConfig
from models.citation import Citation

def validate_citation_data(data: Dict[str, Any], mode: str = "create", current_type: Optional[str] = None, type_change: bool = False):
    """
    Main validation function for citation data.
    
    Args:
        data: Citation data to validate
        mode: Operation mode ("create" or "update")
        current_type: Current citation type (for updates)
        type_change: Whether the citation type is being changed
    
    Returns:
        True if validation passes
        
    Raises:
        HTTPException: If validation fails
    """
    citation_type = _get_citation_type(data, current_type)
    
    _validate_citation_type(citation_type)
    _validate_fields_by_mode_and_type(data, citation_type, mode, current_type, type_change)
    _validate_field_formats(data)
    
    return True

def _get_citation_type(data: Dict[str, Any], current_type: Optional[str]) -> str:
    """Extract and normalize citation type from data or use current type."""
    return (data.get("type") or current_type).lower()

def _validate_citation_type(citation_type: str):
    """Validate that the citation type is supported."""
    config = CitationFieldsConfig()
    if not config.is_valid_type(citation_type):
        raise HTTPException(
            status_code=400, 
            detail=f"Unsupported citation type: {citation_type}. "
                   f"Supported types: {', '.join(config.get_supported_types())}"
        )

def _validate_fields_by_mode_and_type(data: Dict[str, Any], citation_type: str, 
                                    mode: str, current_type: Optional[str], type_change: bool):
    """Validate fields based on operation mode and type change."""
    if mode == "create":
        _validate_create_mode_fields(data, citation_type)
    elif mode == "update" and type_change:
        _validate_update_with_type_change_fields(data, citation_type, current_type)
    elif mode == "update" and not type_change:
        _validate_update_same_type_fields(data, citation_type)

def _validate_create_mode_fields(data: Dict[str, Any], citation_type: str):
    """
    Validate fields for create mode - all required fields must be present and only fields 
    from this type are allowed.
    """
    config = CitationFieldsConfig()
    required_fields = config.get_required_fields(citation_type)
    valid_fields = set(required_fields) 

    # Check for missing required fields (only check if keys are present)
    missing = [field for field in required_fields if field not in data]
    if missing:
        raise HTTPException(
            status_code=400,
            detail=f"Missing required {citation_type} fields: {', '.join(missing)}"
        )
    
    # Check for invalid fields (fields not allowed for this type)
    provided_fields = set(data.keys())
    invalid_fields = provided_fields - valid_fields

    if invalid_fields:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid fields for {citation_type}: {', '.join(invalid_fields)}. "
                   f"Valid fields: {', '.join(sorted(valid_fields))}"
        )

def _validate_update_with_type_change_fields(data: Dict[str, Any], new_type: str, previous_type: str):
    """
    Validate fields when changing citation type - must provide fields that are required 
    in new type but not in previous type. Can also provide other fields from new type.
    """
    config = CitationFieldsConfig()
    new_required_fields = set(config.get_required_fields(new_type))
    previous_required_fields = set(config.get_required_fields(previous_type))
    
    # Get valid fields for the new type
    valid_fields = set(new_required_fields)
    
    # Check for invalid fields (fields not allowed for new type)
    provided_fields = set(data.keys())
    invalid_fields = provided_fields - valid_fields

    if invalid_fields:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid fields for new type {new_type}: {', '.join(invalid_fields)}. "
                   f"Valid fields: {', '.join(sorted(valid_fields))}"
        )
    
    # Find fields that are required in the new type but not in the previous type
    additional_required_fields = new_required_fields - previous_required_fields
    
    # Check if these additional fields are present in the data (only check keys)
    # Exclude 'type' since it's handled separately
    missing = [field for field in additional_required_fields if field not in data and field != "type"]
    
    if missing:
        raise HTTPException(
            status_code=400,
            detail=f"Type change from {previous_type} to {new_type} requires additional fields: {', '.join(missing)}"
        )

def _validate_update_same_type_fields(data: Dict[str, Any], citation_type: str):
    """
    Validate fields for update mode with same type - all provided fields must be 
    valid for the citation type.
    """
    config = CitationFieldsConfig()
    valid_fields = set(config.get_required_fields(citation_type))  
    
    # Check for invalid fields
    provided_fields = set(data.keys())
    invalid_fields = provided_fields - valid_fields
    
    if invalid_fields:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid fields for {citation_type}: {', '.join(invalid_fields)}. "
                   f"Valid fields: {', '.join(sorted(valid_fields))}"
        )

def _validate_field_formats(data: Dict[str, Any]):
    """Validate format of all present fields."""
    field_validators = {
        "authors": _validate_authors,
        "year": _validate_year,
        "title": _validate_non_empty_string,
        "url": _validate_url,
        "doi": _validate_doi,
        "pages": _validate_pages,
        "access_date": _validate_access_date,
        "volume": _validate_volume_edition,
        "issue": _validate_non_empty_string,
        "edition": _validate_volume_edition,
        "publisher": _validate_non_empty_string,
        "place": _validate_non_empty_string,
        "journal": _validate_non_empty_string,
    }
    
    for field, value in data.items():
        if field in field_validators:
            field_validators[field](value, field)

def _validate_authors(authors: Any, field_name: str):
    """Validate authors field - must be a non-empty list of non-empty strings."""
    if not isinstance(authors, list):
        raise HTTPException(status_code=400, detail=f"{field_name.capitalize()} must be a list")
    if not authors:
        raise HTTPException(status_code=400, detail=f"{field_name.capitalize()} list cannot be empty")
    for author in authors:
        if not isinstance(author, str) or not author.strip():
            raise HTTPException(status_code=400, detail=f"All {field_name.lower()} must be non-empty strings")

def _validate_year(year: Any, field_name: str):
    """Validate year field - must be None or a non-negative integer not exceeding current year."""
    if year is None:
        return  # None is valid
    
    if not isinstance(year, int):
        raise HTTPException(status_code=400, detail=f"{field_name.capitalize()} must be an integer or null")
    
    current_year = datetime.now().year
    if year < 0 or year > current_year:
        raise HTTPException(
            status_code=400, 
            detail=f"{field_name.capitalize()} must be a non-negative integer not exceeding {current_year}"
        )

def _validate_url(url: Any, field_name: str):
    """Validate URL field - must be a valid URL format."""
    if not isinstance(url, str):
        raise HTTPException(status_code=400, detail=f"{field_name.upper()} must be a string")
    if not _is_valid_url(url):
        raise HTTPException(status_code=400, detail=f"Invalid {field_name.upper()} format")

def _validate_doi(doi: Any, field_name: str):
    """Validate DOI field - must follow DOI format (10.xxxx/xxxx)."""
    if not isinstance(doi, str):
        raise HTTPException(status_code=400, detail=f"{field_name.upper()} must be a string")
    if not _is_valid_doi(doi):
        raise HTTPException(status_code=400, detail=f"Invalid {field_name.upper()} format (expected: 10.xxxx/xxxx)")

def _validate_pages(pages: Any, field_name: str):
    """Validate pages field - must be in 'start-end' format or multiple ranges."""
    if not isinstance(pages, str):
        raise HTTPException(status_code=400, detail=f"{field_name.capitalize()} must be a string")
    if not _is_valid_pages(pages):
        raise HTTPException(status_code=400, detail=f"{field_name.capitalize()} must be in format 'start-end' or multiple ranges like '1-3, 5-7' (e.g., '123-145' or '1-3, 5-7')")

def _validate_access_date(access_date: Any, field_name: str):
    """Validate access_date field - must be in YYYY-MM-DD format."""
    if not isinstance(access_date, str):
        raise HTTPException(status_code=400, detail=f"{field_name.replace('_', ' ').title()} must be a string")
    if not _is_valid_date(access_date):
        raise HTTPException(
            status_code=400, 
            detail=f"{field_name.replace('_', ' ').title()} must be in YYYY-MM-DD format"
        )

def _validate_volume_edition(value: Any, field_name: str):
    """Validate edition field - must be a positive integer."""
    if not isinstance(value, int):
        raise HTTPException(status_code=400, detail=f"{field_name.capitalize()} must be a positive integer")
    if value <= 0:
        raise HTTPException(status_code=400, detail=f"{field_name.capitalize()} must be a positive integer")

def _validate_non_empty_string(value: Any, field_name: str):
    """Validate string fields that cannot be empty."""
    if not isinstance(value, str) or not value.strip():
        raise HTTPException(status_code=400, detail=f"{field_name.capitalize()} must be a non-empty string")

def _is_valid_url(url: str) -> bool:
    """Check if URL has valid format using regex pattern."""
    url_pattern = re.compile(
        r'^https?://' 
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  
        r'localhost|'  
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' 
        r'(?::\d+)?' 
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    return url_pattern.match(url) is not None

def _is_valid_doi(doi: str) -> bool:
    """Check if DOI has valid format (10.xxxx/xxxx)."""
    doi_pattern = re.compile(r'^10\.\d{4,}/.+$')
    return doi_pattern.match(doi) is not None

def _is_valid_pages(pages: str) -> bool:
    """Check if pages has valid format (number-number) or multiple ranges (1-3, 5-7)."""
    # Pattern for single range: 123-145
    single_range_pattern = r'\d+-\d+'
    # Pattern for multiple ranges separated by comma and optional space: 1-3, 5-7 or 1-3,5-7
    pages_pattern = re.compile(rf'^{single_range_pattern}(?:\s*,\s*{single_range_pattern})*$')
    
    if not pages_pattern.match(pages):
        return False
    
    # Additional validation: ensure each range has start <= end
    ranges = [range_str.strip() for range_str in pages.split(',')]
    for range_str in ranges:
        start, end = map(int, range_str.split('-'))
        if start > end:
            return False
    
    return True

def _is_valid_date(date_str: str) -> bool:
    """Check if date string has valid YYYY-MM-DD format and is a real date."""
    date_pattern = re.compile(r'^\d{4}-\d{2}-\d{2}$')
    if not date_pattern.match(date_str):
        return False
    
    try:
        datetime.strptime(date_str, '%Y-%m-%d')
        return True
    except ValueError:
        return False
