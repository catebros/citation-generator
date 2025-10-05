# backend/tests/test_project_validator.py
import pytest
from fastapi import HTTPException
from services.validators.project_validator import validate_project_data

# Test cases for validate_project_data functionality

def test_validate_project_data_create_valid_passes():
    """Test that valid create data with correct name passes."""
    valid_data = {
        "name": "Valid Project Name"
    }
    
    result = validate_project_data(valid_data, mode="create")
    assert result is True

def test_validate_project_data_create_missing_name_raises_exception():
    """Test that create mode without name raises exception."""
    invalid_data = {}
    
    with pytest.raises(HTTPException) as exc_info:
        validate_project_data(invalid_data, mode="create")
    
    assert exc_info.value.status_code == 400
    assert "Missing required project fields: name" in exc_info.value.detail

def test_validate_project_data_create_invalid_extra_field_raises_exception():
    """Test that create mode with invalid extra field raises exception."""
    invalid_data = {
        "name": "Valid Project Name",
        "invalid_field": "should not be here"
    }
    
    with pytest.raises(HTTPException) as exc_info:
        validate_project_data(invalid_data, mode="create")
    
    assert exc_info.value.status_code == 400
    assert "Invalid fields for project:" in exc_info.value.detail
    assert "invalid_field" in exc_info.value.detail
    assert "Valid fields:" in exc_info.value.detail

def test_validate_project_data_create_empty_name_raises_exception():
    """Test that create mode with empty name raises exception."""
    invalid_data = {
        "name": ""
    }
    
    with pytest.raises(HTTPException) as exc_info:
        validate_project_data(invalid_data, mode="create")
    
    assert exc_info.value.status_code == 400
    assert "Project name must be a non-empty string" in exc_info.value.detail

def test_validate_project_data_create_non_string_name_raises_exception():
    """Test that create mode with non-string name raises exception."""
    invalid_data = {
        "name": 123
    }
    
    with pytest.raises(HTTPException) as exc_info:
        validate_project_data(invalid_data, mode="create")
    
    assert exc_info.value.status_code == 400
    assert "Project name must be a non-empty string" in exc_info.value.detail

def test_validate_project_data_create_none_name_raises_exception():
    """Test that create mode with None name raises exception."""
    invalid_data = {
        "name": None
    }
    
    with pytest.raises(HTTPException) as exc_info:
        validate_project_data(invalid_data, mode="create")
    
    assert exc_info.value.status_code == 400
    assert "Project name must be a non-empty string" in exc_info.value.detail

def test_validate_project_data_update_valid_passes():
    """Test that valid update data with correct name passes."""
    valid_data = {
        "name": "Updated Project Name"
    }
    
    result = validate_project_data(valid_data, mode="update")
    assert result is True

def test_validate_project_data_update_invalid_extra_field_raises_exception():
    """Test that update mode with invalid extra field raises exception."""
    invalid_data = {
        "name": "Valid Project Name",
        "invalid_field": "should not be here"
    }
    
    with pytest.raises(HTTPException) as exc_info:
        validate_project_data(invalid_data, mode="update")
    
    assert exc_info.value.status_code == 400
    assert "Invalid fields for project:" in exc_info.value.detail
    assert "invalid_field" in exc_info.value.detail
    assert "Valid fields:" in exc_info.value.detail

def test_validate_project_data_update_empty_name_raises_exception():
    """Test that update mode with empty name raises exception."""
    invalid_data = {
        "name": ""
    }
    
    with pytest.raises(HTTPException) as exc_info:
        validate_project_data(invalid_data, mode="update")
    
    assert exc_info.value.status_code == 400
    assert "Project name must be a non-empty string" in exc_info.value.detail

def test_validate_project_data_update_non_string_name_raises_exception():
    """Test that update mode with non-string name raises exception."""
    invalid_data = {
        "name": None
    }
    
    with pytest.raises(HTTPException) as exc_info:
        validate_project_data(invalid_data, mode="update")
    
    assert exc_info.value.status_code == 400
    assert "Project name must be a non-empty string" in exc_info.value.detail

def test_validate_project_data_update_whitespace_only_name_raises_exception():
    """Test that update mode with whitespace-only name raises exception."""
    invalid_data = {
        "name": "   "
    }
    
    with pytest.raises(HTTPException) as exc_info:
        validate_project_data(invalid_data, mode="update")
    
    assert exc_info.value.status_code == 400
    assert "Project name must be a non-empty string" in exc_info.value.detail

def test_validate_project_data_update_empty_data_passes():
    """Test that update mode with empty data (no fields to update) passes."""
    valid_data = {}
    
    result = validate_project_data(valid_data, mode="update")
    assert result is True

def test_validate_project_data_create_multiple_invalid_fields_raises_exception():
    """Test that create mode with multiple invalid fields shows all invalid fields."""
    invalid_data = {
        "name": "Valid Project Name",
        "invalid_field1": "value1",
        "invalid_field2": "value2"
    }
    
    with pytest.raises(HTTPException) as exc_info:
        validate_project_data(invalid_data, mode="create")
    
    assert exc_info.value.status_code == 400
    assert "Invalid fields for project:" in exc_info.value.detail
    assert "invalid_field1" in exc_info.value.detail
    assert "invalid_field2" in exc_info.value.detail
    assert "Valid fields:" in exc_info.value.detail

def test_validate_project_data_update_multiple_invalid_fields_raises_exception():
    """Test that update mode with multiple invalid fields shows all invalid fields."""
    invalid_data = {
        "name": "Valid Project Name",
        "invalid_field1": "value1",
        "invalid_field2": "value2"
    }
    
    with pytest.raises(HTTPException) as exc_info:
        validate_project_data(invalid_data, mode="update")
    
    assert exc_info.value.status_code == 400
    assert "Invalid fields for project:" in exc_info.value.detail
    assert "invalid_field1" in exc_info.value.detail
    assert "invalid_field2" in exc_info.value.detail
    assert "Valid fields:" in exc_info.value.detail

# Test cases for project name length validation

def test_validate_project_data_create_name_too_long_raises_exception():
    """Test that create mode with name exceeding maximum length raises exception."""
    from services.validators.project_validator import MAX_PROJECT_NAME_LENGTH
    
    invalid_data = {
        "name": "A" * (MAX_PROJECT_NAME_LENGTH + 1)  # Exceed maximum length
    }
    
    with pytest.raises(HTTPException) as exc_info:
        validate_project_data(invalid_data, mode="create")
    
    assert exc_info.value.status_code == 400
    assert "exceeds maximum length" in exc_info.value.detail
    assert str(MAX_PROJECT_NAME_LENGTH) in exc_info.value.detail

def test_validate_project_data_update_name_too_long_raises_exception():
    """Test that update mode with name exceeding maximum length raises exception."""
    from services.validators.project_validator import MAX_PROJECT_NAME_LENGTH
    
    invalid_data = {
        "name": "B" * (MAX_PROJECT_NAME_LENGTH + 1)  # Exceed maximum length
    }
    
    with pytest.raises(HTTPException) as exc_info:
        validate_project_data(invalid_data, mode="update")
    
    assert exc_info.value.status_code == 400
    assert "exceeds maximum length" in exc_info.value.detail
    assert str(MAX_PROJECT_NAME_LENGTH) in exc_info.value.detail

def test_validate_project_data_create_name_at_maximum_length_passes():
    """Test that create mode with name at exactly maximum length passes."""
    from services.validators.project_validator import MAX_PROJECT_NAME_LENGTH
    
    valid_data = {
        "name": "C" * MAX_PROJECT_NAME_LENGTH  # Exactly at maximum length
    }
    
    result = validate_project_data(valid_data, mode="create")
    assert result is True

def test_validate_project_data_update_name_at_maximum_length_passes():
    """Test that update mode with name at exactly maximum length passes."""
    from services.validators.project_validator import MAX_PROJECT_NAME_LENGTH
    
    valid_data = {
        "name": "D" * MAX_PROJECT_NAME_LENGTH  # Exactly at maximum length
    }
    
    result = validate_project_data(valid_data, mode="update")
    assert result is True

def test_validate_project_data_create_name_one_less_than_maximum_passes():
    """Test that create mode with name one character less than maximum passes."""
    from services.validators.project_validator import MAX_PROJECT_NAME_LENGTH
    
    valid_data = {
        "name": "E" * (MAX_PROJECT_NAME_LENGTH - 1)  # One less than maximum
    }
    
    result = validate_project_data(valid_data, mode="create")
    assert result is True

def test_validate_project_data_update_name_one_less_than_maximum_passes():
    """Test that update mode with name one character less than maximum passes."""
    from services.validators.project_validator import MAX_PROJECT_NAME_LENGTH
    
    valid_data = {
        "name": "F" * (MAX_PROJECT_NAME_LENGTH - 1)  # One less than maximum
    }
    
    result = validate_project_data(valid_data, mode="update")
    assert result is True

def test_validate_project_data_name_with_whitespace_length_validation():
    """Test that name length validation considers trimmed name (whitespace removed)."""
    from services.validators.project_validator import MAX_PROJECT_NAME_LENGTH
    
    # This should pass because after trimming, it's within the limit
    valid_data = {
        "name": "  " + "G" * (MAX_PROJECT_NAME_LENGTH - 2) + "  "  # Whitespace padding
    }
    
    result = validate_project_data(valid_data, mode="create")
    assert result is True
    
    # This should fail because after trimming, it exceeds the limit
    invalid_data = {
        "name": "  " + "H" * (MAX_PROJECT_NAME_LENGTH + 1) + "  "  # Content exceeds limit by 1
    }
    
    with pytest.raises(HTTPException) as exc_info:
        validate_project_data(invalid_data, mode="create")
    
    assert exc_info.value.status_code == 400
    assert "exceeds maximum length" in exc_info.value.detail
