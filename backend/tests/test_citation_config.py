# backend/tests/test_citation_config.py
import pytest
from config.citation_config import CitationFieldsConfig

def test_singleton_behavior():
    """Test that CitationFieldsConfig follows singleton pattern."""
    config1 = CitationFieldsConfig()
    config2 = CitationFieldsConfig()
    assert config1 is config2, "CitationFieldsConfig should return the same instance"

def test_get_required_fields_book():
    """Test get_required_fields returns exact expected list for book."""
    config = CitationFieldsConfig()
    expected_fields = ["type", "title", "authors", "year", "publisher", "place", "edition"]
    actual_fields = config.get_required_fields("book")
    assert actual_fields == expected_fields, f"Expected {expected_fields}, got {actual_fields}"

def test_get_required_fields_article():
    """Test get_required_fields returns exact expected list for article."""
    config = CitationFieldsConfig()
    expected_fields = ["type", "title", "authors", "year", "journal", "volume", "issue", "pages", "doi"]
    actual_fields = config.get_required_fields("article")
    assert actual_fields == expected_fields, f"Expected {expected_fields}, got {actual_fields}"

def test_get_required_fields_website():
    """Test get_required_fields returns exact expected list for website."""
    config = CitationFieldsConfig()
    expected_fields = ["type", "title", "authors", "year", "publisher", "url", "access_date"]
    actual_fields = config.get_required_fields("website")
    assert actual_fields == expected_fields, f"Expected {expected_fields}, got {actual_fields}"

def test_get_required_fields_report():
    """Test get_required_fields returns exact expected list for report."""
    config = CitationFieldsConfig()
    expected_fields = ["type", "title", "authors", "year", "publisher", "url", "place"]
    actual_fields = config.get_required_fields("report")
    assert actual_fields == expected_fields, f"Expected {expected_fields}, got {actual_fields}"

def test_get_required_fields_unsupported_type_raises_keyerror():
    """Test that unsupported types raise KeyError."""
    config = CitationFieldsConfig()
    with pytest.raises(KeyError) as exc_info:
        config.get_required_fields("banana")
    assert "Unsupported citation type: banana" in str(exc_info.value)

def test_is_valid_type_valid_types():
    """Test is_valid_type returns True for valid citation types."""
    config = CitationFieldsConfig()
    valid_types = ["book", "article", "website", "report"]
    
    for citation_type in valid_types:
        assert config.is_valid_type(citation_type), f"Type '{citation_type}' should be valid"

def test_is_valid_type_invalid_types():
    """Test is_valid_type returns False for invalid citation types."""
    config = CitationFieldsConfig()
    invalid_types = ["banana", "movie", "song", "invalid", ""]
    
    for citation_type in invalid_types:
        assert not config.is_valid_type(citation_type), f"Type '{citation_type}' should be invalid"

def test_get_supported_types():
    """Test get_supported_types returns exactly the expected types."""
    config = CitationFieldsConfig()
    expected_types = {"book", "article", "website", "report"}
    actual_types = set(config.get_supported_types())
    assert actual_types == expected_types, f"Expected {expected_types}, got {actual_types}"

def test_data_immutability_required_for_citation_types():
    """Test that returned data from get_required_for_citation_types is immutable."""
    config = CitationFieldsConfig()
    
    # Get the data
    types_dict = config.get_required_for_citation_types()
    
    # Try to modify it
    types_dict["new_type"] = ["field1", "field2"]
    
    # Get fresh data and verify it wasn't modified
    fresh_types_dict = config.get_required_for_citation_types()
    assert "new_type" not in fresh_types_dict, "Returned data should be a copy, not a reference"

def test_data_immutability_get_required_fields():
    """Test that returned data from get_required_fields is immutable."""
    config = CitationFieldsConfig()
    
    # Get the data
    book_fields = config.get_required_fields("book")
    original_length = len(book_fields)
    
    # Try to modify it
    book_fields.append("new_field")
    
    # Get fresh data and verify it wasn't modified
    fresh_book_fields = config.get_required_fields("book")
    assert len(fresh_book_fields) == original_length, "Returned data should be a copy, not a reference"
    assert "new_field" not in fresh_book_fields, "Original data should not be modified"



def test_singleton_initialization_only_once():
    """Test that singleton initialization happens only once."""
    # This test verifies that multiple instantiations don't re-initialize the data
    config1 = CitationFieldsConfig()
    original_types = config1.get_supported_types()
    
    # Create another instance
    config2 = CitationFieldsConfig()
    new_types = config2.get_supported_types()
    
    # Both should return the same data and be the same instance
    assert config1 is config2, "Should be the same instance"
    assert original_types == new_types, "Data should be identical"

def test_all_citation_types_have_required_fields():
    """Test that all supported citation types have required fields defined."""
    config = CitationFieldsConfig()
    supported_types = config.get_supported_types()
    
    for citation_type in supported_types:
        fields = config.get_required_fields(citation_type)
        assert isinstance(fields, list), f"Required fields for {citation_type} should be a list"
        assert len(fields) > 0, f"Required fields for {citation_type} should not be empty"
        assert "type" in fields, f"'type' should be a required field for {citation_type}"
        assert "title" in fields, f"'title' should be a required field for {citation_type}"
        assert "authors" in fields, f"'authors' should be a required field for {citation_type}"
        assert "year" in fields, f"'year' should be a required field for {citation_type}"
