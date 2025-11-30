# backend/tests/test_citation_config.py
import pytest
from config.citation_config import CitationFieldsConfig

def test_singleton_behavior():
    """Test that CitationFieldsConfig follows singleton pattern."""
    config1 = CitationFieldsConfig()
    config2 = CitationFieldsConfig()
    assert config1 is config2, "CitationFieldsConfig should return the same instance"


def test_singleton_has_same_id():
    """Test that multiple CitationFieldsConfig instances have the same ID."""
    config1 = CitationFieldsConfig()
    config2 = CitationFieldsConfig()

    # Both instances should be the exact same object
    assert id(config1) == id(config2), "Singleton instances should have identical IDs"


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


def test_get_required_fields_book():
    """Test get_required_fields returns exact expected list for book."""
    config = CitationFieldsConfig()
    expected_fields = [
        "type",
        "title",
        "authors",
        "year",
        "publisher",
        "place",
        "edition",
    ]
    actual_fields = config.get_required_fields("book")
    assert (
        actual_fields == expected_fields
    ), f"Expected {expected_fields}, got {actual_fields}"


def test_get_required_fields_article():
    """Test get_required_fields returns exact expected list for article."""
    config = CitationFieldsConfig()
    expected_fields = [
        "type",
        "title",
        "authors",
        "year",
        "journal",
        "volume",
        "issue",
        "pages",
        "doi",
    ]
    actual_fields = config.get_required_fields("article")
    assert (
        actual_fields == expected_fields
    ), f"Expected {expected_fields}, got {actual_fields}"


def test_get_required_fields_website():
    """Test get_required_fields returns exact expected list for website."""
    config = CitationFieldsConfig()
    expected_fields = [
        "type",
        "title",
        "authors",
        "year",
        "publisher",
        "url",
        "access_date",
    ]
    actual_fields = config.get_required_fields("website")
    assert (
        actual_fields == expected_fields
    ), f"Expected {expected_fields}, got {actual_fields}"


def test_get_required_fields_report():
    """Test get_required_fields returns exact expected list for report."""
    config = CitationFieldsConfig()
    expected_fields = ["type", "title", "authors", "year", "publisher", "url", "place"]
    actual_fields = config.get_required_fields("report")
    assert (
        actual_fields == expected_fields
    ), f"Expected {expected_fields}, got {actual_fields}"


def test_get_required_fields_unsupported_type_raises_keyerror():
    """Test that unsupported types raise KeyError."""
    config = CitationFieldsConfig()
    with pytest.raises(KeyError) as exc_info:
        config.get_required_fields("banana")
    assert "Unsupported citation type: banana" in str(exc_info.value)


def test_get_required_fields_empty_string_raises_keyerror():
    """Test that empty string type raises KeyError."""
    config = CitationFieldsConfig()
    with pytest.raises(KeyError, match="Unsupported citation type"):
        config.get_required_fields("")


def test_get_required_fields_none_type_raises_keyerror():
    """Test that None type raises KeyError."""
    config = CitationFieldsConfig()
    with pytest.raises(KeyError):
        config.get_required_fields(None)


def test_is_valid_type_valid_types():
    """Test is_valid_type returns True for valid citation types."""
    config = CitationFieldsConfig()
    valid_types = ["book", "article", "website", "report"]

    for citation_type in valid_types:
        assert config.is_valid_type(
            citation_type
        ), f"Type '{citation_type}' should be valid"


def test_is_valid_type_invalid_types():
    """Test is_valid_type returns False for invalid citation types."""
    config = CitationFieldsConfig()
    invalid_types = ["banana", "movie", "song", "invalid", ""]

    for citation_type in invalid_types:
        assert not config.is_valid_type(
            citation_type
        ), f"Type '{citation_type}' should be invalid"


def test_is_valid_type_case_sensitive():
    """Test that is_valid_type is case-sensitive."""
    config = CitationFieldsConfig()

    # Valid types are lowercase
    assert config.is_valid_type("book") is True
    assert config.is_valid_type("BOOK") is False
    assert config.is_valid_type("Book") is False
    assert config.is_valid_type("article") is True
    assert config.is_valid_type("ARTICLE") is False


def test_is_valid_type_with_none():
    """Test is_valid_type returns False for None."""
    config = CitationFieldsConfig()
    # is_valid_type uses "in" operator which handles None gracefully
    assert config.is_valid_type(None) is False


def test_get_supported_types():
    """Test get_supported_types returns exactly the expected types."""
    config = CitationFieldsConfig()
    expected_types = {"book", "article", "website", "report"}
    actual_types = set(config.get_supported_types())
    assert (
        actual_types == expected_types
    ), f"Expected {expected_types}, got {actual_types}"


def test_get_supported_types_returns_list():
    """Test that get_supported_types returns a list."""
    config = CitationFieldsConfig()
    supported_types = config.get_supported_types()

    assert isinstance(supported_types, list), "Should return a list"
    assert len(supported_types) == 4, "Should have exactly 4 supported types"


def test_get_supported_types_has_all_types():
    """Test that get_supported_types includes all expected types."""
    config = CitationFieldsConfig()
    supported_types = config.get_supported_types()

    assert "book" in supported_types
    assert "article" in supported_types
    assert "website" in supported_types
    assert "report" in supported_types


def test_get_required_for_citation_types_returns_dict():
    """Test that get_required_for_citation_types returns a dictionary."""
    config = CitationFieldsConfig()
    all_requirements = config.get_required_for_citation_types()

    assert isinstance(all_requirements, dict), "Should return a dictionary"
    assert len(all_requirements) == 4, "Should have exactly 4 citation types"


def test_get_required_for_citation_types_has_all_types():
    """Test that get_required_for_citation_types includes all types."""
    config = CitationFieldsConfig()
    all_requirements = config.get_required_for_citation_types()

    assert "book" in all_requirements
    assert "article" in all_requirements
    assert "website" in all_requirements
    assert "report" in all_requirements


def test_get_required_for_citation_types_each_has_fields():
    """Test that each type in get_required_for_citation_types has required fields."""
    config = CitationFieldsConfig()
    all_requirements = config.get_required_for_citation_types()

    for citation_type, fields in all_requirements.items():
        assert isinstance(fields, list), f"{citation_type} should have a list of fields"
        assert (
            len(fields) > 0
        ), f"{citation_type} should have at least one required field"


def test_data_immutability_required_for_citation_types():
    """Test that returned data from get_required_for_citation_types is immutable."""
    config = CitationFieldsConfig()

    # Get the data
    types_dict = config.get_required_for_citation_types()

    # Try to modify it
    types_dict["new_type"] = ["field1", "field2"]

    # Get fresh data and verify it wasn't modified
    fresh_types_dict = config.get_required_for_citation_types()
    assert (
        "new_type" not in fresh_types_dict
    ), "Returned data should be a copy, not a reference"


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
    assert (
        len(fresh_book_fields) == original_length
    ), "Returned data should be a copy, not a reference"
    assert "new_field" not in fresh_book_fields, "Original data should not be modified"


def test_data_immutability_get_supported_types():
    """Test that returned data from get_supported_types is immutable."""
    config = CitationFieldsConfig()

    # Get the data
    supported_types = config.get_supported_types()
    original_length = len(supported_types)

    # Try to modify it
    supported_types.append("fake_type")

    # Get fresh data and verify it wasn't modified
    fresh_types = config.get_supported_types()
    assert len(fresh_types) == original_length, "Returned data should be a copy"
    assert "fake_type" not in fresh_types, "Original data should not be modified"


def test_data_immutability_nested_list_modification():
    """Test that modifying nested lists doesn't affect internal data."""
    config = CitationFieldsConfig()

    # Get all requirements
    all_requirements = config.get_required_for_citation_types()

    # Try to modify the nested list for book
    all_requirements["book"].append("fake_field")

    # Get fresh data and verify nested list wasn't modified
    fresh_book_fields = config.get_required_fields("book")
    assert "fake_field" not in fresh_book_fields, "Nested list should not be modified"

def test_all_citation_types_have_required_fields():
    """Test that all supported citation types have required fields defined."""
    config = CitationFieldsConfig()
    supported_types = config.get_supported_types()

    for citation_type in supported_types:
        fields = config.get_required_fields(citation_type)
        assert isinstance(
            fields, list
        ), f"Required fields for {citation_type} should be a list"
        assert (
            len(fields) > 0
        ), f"Required fields for {citation_type} should not be empty"
        assert (
            "type" in fields
        ), f"'type' should be a required field for {citation_type}"
        assert (
            "title" in fields
        ), f"'title' should be a required field for {citation_type}"
        assert (
            "authors" in fields
        ), f"'authors' should be a required field for {citation_type}"
        assert (
            "year" in fields
        ), f"'year' should be a required field for {citation_type}"


def test_all_required_fields_are_strings():
    """Test that all required field names are strings."""
    config = CitationFieldsConfig()
    all_requirements = config.get_required_for_citation_types()

    for citation_type, fields in all_requirements.items():
        for field in fields:
            assert isinstance(
                field, str
            ), f"Field '{field}' in {citation_type} should be a string"
            assert len(field) > 0, f"Field name in {citation_type} should not be empty"


def test_no_duplicate_fields_in_any_type():
    """Test that no citation type has duplicate field names."""
    config = CitationFieldsConfig()
    all_requirements = config.get_required_for_citation_types()

    for citation_type, fields in all_requirements.items():
        unique_fields = set(fields)
        assert len(unique_fields) == len(
            fields
        ), f"{citation_type} should not have duplicate fields"


def test_common_fields_across_all_types():
    """Test that all types share common required fields."""
    config = CitationFieldsConfig()
    all_requirements = config.get_required_for_citation_types()

    # These fields should be required for all citation types
    common_fields = {"type", "title", "authors", "year"}

    for citation_type, fields in all_requirements.items():
        fields_set = set(fields)
        assert common_fields.issubset(
            fields_set
        ), f"{citation_type} should have all common fields: {common_fields}"


def test_type_specific_fields():
    """Test that each citation type has its specific required fields."""
    config = CitationFieldsConfig()

    # Book-specific
    book_fields = set(config.get_required_fields("book"))
    assert "publisher" in book_fields
    assert "place" in book_fields
    assert "edition" in book_fields

    # Article-specific
    article_fields = set(config.get_required_fields("article"))
    assert "journal" in article_fields
    assert "volume" in article_fields
    assert "doi" in article_fields

    # Website-specific
    website_fields = set(config.get_required_fields("website"))
    assert "url" in website_fields
    assert "access_date" in website_fields

    # Report-specific
    report_fields = set(config.get_required_fields("report"))
    assert "url" in report_fields
    assert "place" in report_fields
