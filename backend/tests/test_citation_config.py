import pytest
from config.citation_config import CitationConfig


def test_singleton_behavior():
    """Test that CitationConfig follows singleton pattern."""
    config1 = CitationConfig()
    config2 = CitationConfig()
    assert config1 is config2, "CitationConfig should return the same instance"

def test_get_required_fields_book():
    """Test get_required_fields returns exact expected list for book."""
    config = CitationConfig()
    expected_fields = ["type", "title", "authors", "year", "publisher", "place", "edition"]
    actual_fields = config.get_required_fields("book")
    assert actual_fields == expected_fields, f"Expected {expected_fields}, got {actual_fields}"

def test_get_required_fields_article():
    """Test get_required_fields returns exact expected list for article."""
    config = CitationConfig()
    expected_fields = ["type", "title", "authors", "year", "journal", "volume", "issue", "pages", "doi"]
    actual_fields = config.get_required_fields("article")
    assert actual_fields == expected_fields, f"Expected {expected_fields}, got {actual_fields}"

def test_get_required_fields_website():
    """Test get_required_fields returns exact expected list for website."""
    config = CitationConfig()
    expected_fields = ["type", "title", "authors", "year", "publisher", "url", "access_date"]
    actual_fields = config.get_required_fields("website")
    assert actual_fields == expected_fields, f"Expected {expected_fields}, got {actual_fields}"

def test_get_required_fields_report():
    """Test get_required_fields returns exact expected list for report."""
    config = CitationConfig()
    expected_fields = ["type", "title", "authors", "year", "publisher", "url", "place"]
    actual_fields = config.get_required_fields("report")
    assert actual_fields == expected_fields, f"Expected {expected_fields}, got {actual_fields}"

def test_get_required_fields_unsupported_type_raises_keyerror():
    """Test that unsupported types raise KeyError."""
    config = CitationConfig()
    with pytest.raises(KeyError) as exc_info:
        config.get_required_fields("banana")
    assert "Unsupported citation type: banana" in str(exc_info.value)

def test_all_fields_contains_expected_fields():
    """Test that get_all_fields contains all possible fields."""
    config = CitationConfig()
    expected_fields = [
        "type", "title", "authors", "year", "publisher", "place", "edition",
        "journal", "volume", "issue", "pages", "doi", "url", "access_date"
    ]
    actual_fields = config.get_all_fields()
    assert set(actual_fields) == set(expected_fields), f"Expected {expected_fields}, got {actual_fields}"
    assert len(actual_fields) == len(expected_fields), "All fields list should not contain duplicates"

def test_is_valid_field_valid_fields():
    """Test is_valid_field returns True for valid fields."""
    config = CitationConfig()
    valid_fields = ["title", "authors", "year", "publisher", "journal", "volume", "issue", 
                   "pages", "doi", "url", "access_date", "place", "edition", "type"]
    
    for field in valid_fields:
        assert config.is_valid_field(field), f"Field '{field}' should be valid"

def test_is_valid_field_invalid_fields():
    """Test is_valid_field returns False for invalid fields."""
    config = CitationConfig()
    invalid_fields = ["nonsense", "banana", "invalid", "random", ""]
    
    for field in invalid_fields:
        assert not config.is_valid_field(field), f"Field '{field}' should be invalid"

def test_is_valid_type_valid_types():
    """Test is_valid_type returns True for valid citation types."""
    config = CitationConfig()
    valid_types = ["book", "article", "website", "report"]
    
    for citation_type in valid_types:
        assert config.is_valid_type(citation_type), f"Type '{citation_type}' should be valid"

def test_is_valid_type_invalid_types():
    """Test is_valid_type returns False for invalid citation types."""
    config = CitationConfig()
    invalid_types = ["banana", "movie", "song", "invalid", ""]
    
    for citation_type in invalid_types:
        assert not config.is_valid_type(citation_type), f"Type '{citation_type}' should be invalid"

def test_get_supported_types():
    """Test get_supported_types returns exactly the expected types."""
    config = CitationConfig()
    expected_types = {"book", "article", "website", "report"}
    actual_types = set(config.get_supported_types())
    assert actual_types == expected_types, f"Expected {expected_types}, got {actual_types}"

def test_data_immutability_required_for_citation_types():
    """Test that returned data from get_required_for_citation_types is immutable."""
    config = CitationConfig()
    
    # Get the data
    types_dict = config.get_required_for_citation_types()
    
    # Try to modify it
    types_dict["new_type"] = ["field1", "field2"]
    
    # Get fresh data and verify it wasn't modified
    fresh_types_dict = config.get_required_for_citation_types()
    assert "new_type" not in fresh_types_dict, "Returned data should be a copy, not a reference"

def test_data_immutability_all_fields():
    """Test that returned data from get_all_fields is immutable."""
    config = CitationConfig()
    
    # Get the data
    fields_list = config.get_all_fields()
    original_length = len(fields_list)
    
    # Try to modify it
    fields_list.append("new_field")
    
    # Get fresh data and verify it wasn't modified
    fresh_fields_list = config.get_all_fields()
    assert len(fresh_fields_list) == original_length, "Returned data should be a copy, not a reference"
    assert "new_field" not in fresh_fields_list, "Original data should not be modified"

def test_data_immutability_get_required_fields():
    """Test that returned data from get_required_fields is immutable."""
    config = CitationConfig()
    
    # Get the data
    book_fields = config.get_required_fields("book")
    original_length = len(book_fields)
    
    # Try to modify it
    book_fields.append("new_field")
    
    # Get fresh data and verify it wasn't modified
    fresh_book_fields = config.get_required_fields("book")
    assert len(fresh_book_fields) == original_length, "Returned data should be a copy, not a reference"
    assert "new_field" not in fresh_book_fields, "Original data should not be modified"

def test_backwards_compatibility_constants():
    """Test that global constants are still available for backwards compatibility."""
    from config.citation_config import REQUIRED_FOR_CITATION_TYPES, ALL_FIELDS
    
    # Test REQUIRED_FOR_CITATION_TYPES
    assert isinstance(REQUIRED_FOR_CITATION_TYPES, dict), "REQUIRED_FOR_CITATION_TYPES should be a dict"
    assert "book" in REQUIRED_FOR_CITATION_TYPES, "book should be in REQUIRED_FOR_CITATION_TYPES"
    assert "article" in REQUIRED_FOR_CITATION_TYPES, "article should be in REQUIRED_FOR_CITATION_TYPES"
    
    # Test ALL_FIELDS
    assert isinstance(ALL_FIELDS, list), "ALL_FIELDS should be a list"
    assert "title" in ALL_FIELDS, "title should be in ALL_FIELDS"
    assert "authors" in ALL_FIELDS, "authors should be in ALL_FIELDS"

def test_singleton_initialization_only_once():
    """Test that singleton initialization happens only once."""
    # This test verifies that multiple instantiations don't re-initialize the data
    config1 = CitationConfig()
    original_types = config1.get_supported_types()
    
    # Create another instance
    config2 = CitationConfig()
    new_types = config2.get_supported_types()
    
    # Both should return the same data and be the same instance
    assert config1 is config2, "Should be the same instance"
    assert original_types == new_types, "Data should be identical"

def test_all_citation_types_have_required_fields():
    """Test that all supported citation types have required fields defined."""
    config = CitationConfig()
    supported_types = config.get_supported_types()
    
    for citation_type in supported_types:
        fields = config.get_required_fields(citation_type)
        assert isinstance(fields, list), f"Required fields for {citation_type} should be a list"
        assert len(fields) > 0, f"Required fields for {citation_type} should not be empty"
        assert "type" in fields, f"'type' should be a required field for {citation_type}"
        assert "title" in fields, f"'title' should be a required field for {citation_type}"
        assert "authors" in fields, f"'authors' should be a required field for {citation_type}"
        assert "year" in fields, f"'year' should be a required field for {citation_type}"