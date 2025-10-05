# backend/services/validators/citation_validator.py
from fastapi import HTTPException
import re
from datetime import datetime
from typing import Dict, List, Any, Optional
from config.citation_config import CitationFieldsConfig
from models.citation import Citation

# String length limits for validation
# These limits are generous to accommodate edge cases while preventing abuse
MAX_TITLE_LENGTH = 500  # Maximum characters for citation titles
MAX_AUTHOR_NAME_LENGTH = 150  # Maximum characters for individual author names
MAX_PUBLISHER_LENGTH = 200  # Maximum characters for publisher names
MAX_JOURNAL_LENGTH = 200  # Maximum characters for journal names
MAX_PLACE_LENGTH = 100  # Maximum characters for place names
MAX_URL_LENGTH = 2000  # Maximum characters for URLs
MAX_DOI_LENGTH = 300  # Maximum characters for DOI identifiers
MAX_PAGES_LENGTH = 50  # Maximum characters for page ranges
MAX_ISSUE_LENGTH = 50  # Maximum characters for issue identifiers

def validate_citation_data(data: Dict[str, Any], mode: str = "create", current_type: Optional[str] = None, type_change: bool = False) -> bool:
    """
    Main validation function for citation data with comprehensive field checking.

    This function coordinates all citation validation logic including:
    - Citation type validation
    - Mode-specific field requirements (create vs update)
    - Type change handling with additional field requirements
    - Format validation for all field types

    Args:
        data (Dict[str, Any]): Citation data to validate
        mode (str): Operation mode ("create" or "update"), defaults to "create"
        current_type (Optional[str]): Current citation type (required for updates)
        type_change (bool): Whether the citation type is being changed

    Returns:
        bool: True if validation passes

    Raises:
        HTTPException: 400 with detailed error message if validation fails

    Note:
        - Create mode requires all fields for the citation type
        - Update mode allows partial updates for the same type
        - Type changes require additional fields specific to the new type
        - All string fields are validated for length and format
    """
    citation_type = _get_citation_type(data, current_type)
    
    _validate_citation_type(citation_type)
    _validate_fields_by_mode_and_type(data, citation_type, mode, current_type, type_change)
    _validate_field_formats(data)
    
    return True

def _get_citation_type(data: Dict[str, Any], current_type: Optional[str]) -> str:
    """
    Extract and normalize citation type from data or use current type.

    Args:
        data (Dict[str, Any]): Citation data dictionary
        current_type (Optional[str]): Current citation type (for updates)

    Returns:
        str: Normalized citation type in lowercase
    """
    return (data.get("type") or current_type).lower()

def _validate_citation_type(citation_type: str) -> None:
    """
    Validate that the citation type is supported by the system.

    Args:
        citation_type (str): Citation type to validate

    Raises:
        HTTPException: 400 if citation type is not supported

    Note:
        - Supported types are defined in CitationFieldsConfig
        - Error message includes list of supported types
    """
    config = CitationFieldsConfig()
    if not config.is_valid_type(citation_type):
        raise HTTPException(
            status_code=400, 
            detail=f"Unsupported citation type: {citation_type}. "
                   f"Supported types: {', '.join(config.get_supported_types())}"
        )

def _validate_fields_by_mode_and_type(data: Dict[str, Any], citation_type: str,
                                    mode: str, current_type: Optional[str], type_change: bool) -> None:
    """
    Route to appropriate field validation based on operation mode and type change.

    Args:
        data (Dict[str, Any]): Citation data to validate
        citation_type (str): The citation type being used
        mode (str): Operation mode ("create" or "update")
        current_type (Optional[str]): Current citation type (for updates)
        type_change (bool): Whether the type is being changed

    Note:
        - Routes to different validators based on mode and type_change
        - Create mode validates all required fields
        - Update with type change validates additional required fields
        - Update without type change validates only provided fields
    """
    if mode == "create":
        _validate_create_mode_fields(data, citation_type)
    elif mode == "update" and type_change:
        _validate_update_with_type_change_fields(data, citation_type, current_type)
    elif mode == "update" and not type_change:
        _validate_update_same_type_fields(data, citation_type)

def _validate_create_mode_fields(data: Dict[str, Any], citation_type: str) -> None:
    """
    Validate fields for create mode with strict requirements.

    For creation, all required fields for the citation type must be present,
    and no invalid fields should be included.

    Args:
        data (Dict[str, Any]): Citation data to validate
        citation_type (str): The type of citation being created

    Raises:
        HTTPException: 400 if required fields are missing or invalid fields are present

    Note:
        - Checks that all required fields are present (not their values)
        - Rejects any fields not valid for this citation type
        - Required fields vary by citation type
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

def _validate_update_with_type_change_fields(data: Dict[str, Any], new_type: str, previous_type: str) -> None:
    """
    Validate fields when changing citation type during update.

    When changing types, the user must provide any fields that are required
    in the new type but weren't required in the previous type.

    Args:
        data (Dict[str, Any]): Citation update data
        new_type (str): New citation type being applied
        previous_type (str): Current citation type before change

    Raises:
        HTTPException: 400 if invalid fields are provided or required new fields are missing

    Note:
        - Must provide fields required by new type but not by previous type
        - Can provide any other valid fields for the new type
        - Fields from previous type not in new type will be set to None
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

def _validate_update_same_type_fields(data: Dict[str, Any], citation_type: str) -> None:
    """
    Validate fields for update mode without type change.

    When updating without changing type, partial updates are allowed.
    Only validates that provided fields are valid for the citation type.

    Args:
        data (Dict[str, Any]): Citation update data (can be partial)
        citation_type (str): The citation type (unchanged)

    Raises:
        HTTPException: 400 if any provided fields are invalid for this type

    Note:
        - Allows partial updates (not all fields required)
        - Only checks that provided fields are valid for the type
        - Does not require missing fields to be provided
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

def _validate_field_formats(data: Dict[str, Any]) -> None:
    """
    Validate format and content of all present fields.

    This function routes each field to its specific validator based on
    the field name. Validates data types, formats, and content constraints.

    Args:
        data (Dict[str, Any]): Citation data with fields to validate

    Raises:
        HTTPException: 400 if any field has invalid format or content

    Note:
        - Only validates fields that are present in data
        - Each field type has specific validation rules
        - String fields are checked for length limits
        - URLs, DOIs, dates, etc. are validated against patterns
    """
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
        "place": _validate_place,
        "journal": _validate_non_empty_string,
    }
    
    for field, value in data.items():
        if field in field_validators:
            field_validators[field](value, field)

def _validate_authors(authors: Any, field_name: str) -> None:
    """
    Validate authors field format and content.

    Authors must be a non-empty list of valid author name strings.
    Each author name is validated for format and length.

    Args:
        authors (Any): Value to validate as authors list
        field_name (str): Field name for error messages

    Raises:
        HTTPException: 400 if authors is not a list, is empty, or contains invalid names

    Note:
        - Must be a list (not string or other type)
        - List cannot be empty
        - Each author must be a non-empty string
        - Author names can only contain letters, spaces, hyphens, apostrophes, periods
        - Each author name limited to MAX_AUTHOR_NAME_LENGTH characters
    """
    if not isinstance(authors, list):
        raise HTTPException(status_code=400, detail=f"{field_name.capitalize()} must be a list")
    if not authors:
        raise HTTPException(status_code=400, detail=f"{field_name.capitalize()} list cannot be empty")
    for author in authors:
        if not isinstance(author, str) or not author.strip():
            raise HTTPException(status_code=400, detail=f"All {field_name.lower()} must be non-empty strings")
        if len(author.strip()) > MAX_AUTHOR_NAME_LENGTH:
            raise HTTPException(status_code=400, detail=f"Author name exceeds maximum length of {MAX_AUTHOR_NAME_LENGTH} characters")
        if not _is_valid_name(author.strip()):
            raise HTTPException(status_code=400, detail=f"Author names can only contain letters, spaces, hyphens, apostrophes, and periods")

def _validate_year(year: Any, field_name: str) -> None:
    """
    Validate year field format and range.

    Args:
        year (Any): Value to validate as year
        field_name (str): Field name for error messages

    Raises:
        HTTPException: 400 if year is not an integer, is negative, or exceeds current year

    Note:
        - None is valid (allows missing publication years)
        - Must be an integer (not string)
        - Cannot be negative
        - Cannot exceed current year
    """
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

def _validate_url(url: Any, field_name: str) -> None:
    """Validate URL field - must be a valid URL format."""
    if not isinstance(url, str):
        raise HTTPException(status_code=400, detail=f"{field_name.upper()} must be a string")
    if len(url) > MAX_URL_LENGTH:
        raise HTTPException(status_code=400, detail=f"{field_name.upper()} exceeds maximum length of {MAX_URL_LENGTH} characters")
    if not _is_valid_url(url):
        raise HTTPException(status_code=400, detail=f"Invalid {field_name.upper()} format")

def _validate_doi(doi: Any, field_name: str) -> None:
    """Validate DOI field - must follow DOI format (10.xxxx/xxxx)."""
    if not isinstance(doi, str):
        raise HTTPException(status_code=400, detail=f"{field_name.upper()} must be a string")
    if len(doi) > MAX_DOI_LENGTH:
        raise HTTPException(status_code=400, detail=f"{field_name.upper()} exceeds maximum length of {MAX_DOI_LENGTH} characters")
    if not _is_valid_doi(doi):
        raise HTTPException(status_code=400, detail=f"Invalid {field_name.upper()} format (expected: 10.xxxx/xxxx)")

def _validate_pages(pages: Any, field_name: str) -> None:
    """Validate pages field - must be in 'start-end' format or multiple ranges."""
    if not isinstance(pages, str):
        raise HTTPException(status_code=400, detail=f"{field_name.capitalize()} must be a string")
    if len(pages) > MAX_PAGES_LENGTH:
        raise HTTPException(status_code=400, detail=f"{field_name.capitalize()} exceeds maximum length of {MAX_PAGES_LENGTH} characters")
    if not _is_valid_pages(pages):
        raise HTTPException(status_code=400, detail=f"{field_name.capitalize()} must be in format 'start-end' or multiple ranges like '1-3, 5-7' (e.g., '123-145' or '1-3, 5-7')")

def _validate_access_date(access_date: Any, field_name: str) -> None:
    """Validate access_date field - must be in YYYY-MM-DD format."""
    if not isinstance(access_date, str):
        raise HTTPException(status_code=400, detail=f"{field_name.replace('_', ' ').title()} must be a string")
    if not _is_valid_date(access_date):
        raise HTTPException(
            status_code=400, 
            detail=f"{field_name.replace('_', ' ').title()} must be in YYYY-MM-DD format"
        )

def _validate_volume_edition(value: Any, field_name: str) -> None:
    """Validate edition field - must be a positive integer."""
    if not isinstance(value, int):
        raise HTTPException(status_code=400, detail=f"{field_name.capitalize()} must be a positive integer")
    if value <= 0:
        raise HTTPException(status_code=400, detail=f"{field_name.capitalize()} must be a positive integer")

def _validate_place(place: Any, field_name: str) -> None:
    """Validate place field - must be a non-empty string without numbers or special characters."""
    if not isinstance(place, str) or not place.strip():
        raise HTTPException(status_code=400, detail=f"{field_name.capitalize()} must be a non-empty string")
    if len(place.strip()) > MAX_PLACE_LENGTH:
        raise HTTPException(status_code=400, detail=f"{field_name.capitalize()} exceeds maximum length of {MAX_PLACE_LENGTH} characters")
    if not _is_valid_place_name(place.strip()):
        raise HTTPException(status_code=400, detail=f"Place names can only contain letters, spaces, hyphens, apostrophes, periods, and commas")

def _validate_non_empty_string(value: Any, field_name: str) -> None:
    """Validate string fields that cannot be empty."""
    if not isinstance(value, str) or not value.strip():
        raise HTTPException(status_code=400, detail=f"{field_name.capitalize()} must be a non-empty string")
    _validate_string_length(value.strip(), field_name)

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

def _is_valid_name(name: str) -> bool:
    """Check if name contains only valid characters (letters, spaces, hyphens, apostrophes, periods)."""
    # Allow letters (including accented), spaces, hyphens, apostrophes, and periods
    # Exclude numbers and special characters like @, #, $, etc.
    name_pattern = re.compile(r"^[a-zA-ZÀ-ÿ\s\-\'\.']+$")
    return name_pattern.match(name) is not None

def _is_valid_place_name(place: str) -> bool:
    """Check if place name contains only valid characters (letters, spaces, hyphens, apostrophes, periods, commas)."""
    # Allow letters (including accented), spaces, hyphens, apostrophes, periods, and commas for places
    # Exclude numbers and special characters like @, #, $, etc.
    place_pattern = re.compile(r"^[a-zA-ZÀ-ÿ\s\-\'\.',]+$")
    return place_pattern.match(place) is not None

def _validate_string_length(value: str, field_name: str) -> None:
    """Validate string length based on field type."""
    length_limits = {
        "title": MAX_TITLE_LENGTH,
        "publisher": MAX_PUBLISHER_LENGTH,
        "journal": MAX_JOURNAL_LENGTH,
        "issue": MAX_ISSUE_LENGTH,
    }
    
    max_length = length_limits.get(field_name.lower())
    if max_length and len(value) > max_length:
        raise HTTPException(
            status_code=400, 
            detail=f"{field_name.capitalize()} exceeds maximum length of {max_length} characters"
        )
