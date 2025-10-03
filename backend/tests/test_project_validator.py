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
