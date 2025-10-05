# backend/tests/test_citation_validator.py
"""
Test suite for citation_validator module.

This module contains comprehensive tests for citation data validation including:
- Citation type validation (book, article, website, report)
- Field requirement validation for create/update modes
- Type change validation with additional field requirements
- Field format validation (authors, year, title, URL, DOI, pages, dates)
- Character validation (valid characters, accents, special characters)
- Length validation for all string fields with max length limits
- Edge cases (None values, empty strings, whitespace, boundary conditions)

The validation logic ensures data integrity before citations are stored in the database.
"""
import pytest
from fastapi import HTTPException
from services.validators.citation_validator import validate_citation_data

# ========== GENERAL FUNCTIONALITY TESTS ==========

def test_validate_citation_data_supported_type_passes():
    """Test that supported citation types pass validation."""
    # Valid book citation with all required fields
    valid_data = {
        "type": "book",
        "title": "Test Book",
        "authors": ["Author One"],
        "year": 2023,
        "publisher": "Test Publisher",
        "place": "Test City",
        "edition": 1
    }

    # Should not raise exception
    result = validate_citation_data(valid_data, mode="create")
    assert result is True

def test_validate_citation_data_unsupported_type_raises_exception():
    """Test that unsupported citation types raise HTTPException."""
    invalid_data = {
        "type": "invalid_type",
        "title": "Test",
        "authors": ["Author"]
    }
    
    with pytest.raises(HTTPException) as exc_info:
        validate_citation_data(invalid_data, mode="create")
    
    assert exc_info.value.status_code == 400
    assert "Unsupported citation type: invalid_type" in exc_info.value.detail
    assert "Supported types:" in exc_info.value.detail

def test_validate_citation_data_create_mode_valid_passes():
    """Test that valid create mode data passes."""
    valid_data = {
        "type": "article",
        "title": "Test Article",
        "authors": ["Author One"],
        "year": 2023,
        "journal": "Test Journal",
        "volume": 1,
        "issue": "1",
        "pages": "1-10",
        "doi": "10.1234/test.2023"
    }
    
    result = validate_citation_data(valid_data, mode="create")
    assert result is True

def test_validate_citation_data_create_mode_missing_fields_raises_exception():
    """Test that create mode with missing required fields raises exception."""
    incomplete_data = {
        "type": "book",
        "authors": ["Author One"]
        # Missing title and publisher
    }
    
    with pytest.raises(HTTPException) as exc_info:
        validate_citation_data(incomplete_data, mode="create")
    
    assert exc_info.value.status_code == 400
    assert "Missing required book fields:" in exc_info.value.detail

def test_validate_citation_data_create_mode_invalid_field_raises_exception():
    """Test that create mode with invalid extra field raises exception."""
    invalid_data = {
        "type": "book",
        "title": "Test Book",
        "authors": ["Author One"],
        "year": 2023,
        "publisher": "Test Publisher",
        "place": "Test City",
        "edition": 1,
        "invalid_field": "should not be here"
    }
    
    with pytest.raises(HTTPException) as exc_info:
        validate_citation_data(invalid_data, mode="create")
    
    assert exc_info.value.status_code == 400
    assert "Invalid fields for book:" in exc_info.value.detail
    assert "invalid_field" in exc_info.value.detail

def test_validate_citation_data_update_same_type_valid_passes():
    """Test that update mode with same type and valid fields passes."""
    valid_data = {
        "title": "Updated Title",
        "year": 2024
    }
    
    result = validate_citation_data(valid_data, mode="update", current_type="book", type_change=False)
    assert result is True

def test_validate_citation_data_update_same_type_invalid_field_raises_exception():
    """Test that update mode with invalid field raises exception."""
    invalid_data = {
        "title": "Updated Title",
        "invalid_field": "should not be here"
    }
    
    with pytest.raises(HTTPException) as exc_info:
        validate_citation_data(invalid_data, mode="update", current_type="book", type_change=False)
    
    assert exc_info.value.status_code == 400
    assert "Invalid fields for book:" in exc_info.value.detail

def test_validate_citation_data_type_change_valid_passes():
    """Test that valid type change with required additional fields passes."""
    valid_data = {
        "type": "article",
        "journal": "Test Journal",
        "volume": 1,
        "issue": "1",
        "pages": "1-10",
        "doi": "10.1234/test.2023"
    }
    
    result = validate_citation_data(valid_data, mode="update", current_type="book", type_change=True)
    assert result is True

def test_validate_citation_data_type_change_missing_required_raises_exception():
    """Test that type change missing required fields raises exception."""
    invalid_data = {
        "type": "article"
        # Missing journal, volume, issue, pages required for article
    }
    
    with pytest.raises(HTTPException) as exc_info:
        validate_citation_data(invalid_data, mode="update", current_type="book", type_change=True)
    
    assert exc_info.value.status_code == 400
    assert "Type change from book to article requires additional fields:" in exc_info.value.detail

# ========== FIELD FORMAT VALIDATION TESTS ==========

def test_validate_authors_valid_list_passes():
    """Test that valid authors list passes validation."""
    valid_data = {
        "type": "book",
        "title": "Test Book",
        "authors": ["Author One", "Author Two"],
        "year": 2023,
        "publisher": "Test Publisher",
        "place": "Test City",
        "edition": 1
    }
    
    result = validate_citation_data(valid_data, mode="create")
    assert result is True

def test_validate_authors_not_list_raises_exception():
    """Test that authors not being a list raises exception."""
    invalid_data = {
        "type": "book",
        "title": "Test Book",
        "authors": "Not a list",
        "year": 2023,
        "publisher": "Test Publisher",
        "place": "Test City",
        "edition": 1
    }
    
    with pytest.raises(HTTPException) as exc_info:
        validate_citation_data(invalid_data, mode="create")
    
    assert exc_info.value.status_code == 400
    assert "Authors must be a list" in exc_info.value.detail

def test_validate_authors_empty_list_raises_exception():
    """Test that empty authors list raises exception."""
    invalid_data = {
        "type": "book",
        "title": "Test Book",
        "authors": [],
        "year": 2023,
        "publisher": "Test Publisher",
        "place": "Test City",
        "edition": 1
    }
    
    with pytest.raises(HTTPException) as exc_info:
        validate_citation_data(invalid_data, mode="create")
    
    assert exc_info.value.status_code == 400
    assert "Authors list cannot be empty" in exc_info.value.detail

def test_validate_authors_empty_string_raises_exception():
    """Test that authors containing empty string raises exception."""
    invalid_data = {
        "type": "book",
        "title": "Test Book",
        "authors": ["Author One", ""],
        "year": 2023,
        "publisher": "Test Publisher",
        "place": "Test City",
        "edition": 1
    }
    
    with pytest.raises(HTTPException) as exc_info:
        validate_citation_data(invalid_data, mode="create")
    
    assert exc_info.value.status_code == 400
    assert "All authors must be non-empty strings" in exc_info.value.detail

def test_validate_year_valid_integer_passes():
    """Test that valid year integer passes validation."""
    valid_data = {
        "type": "book",
        "title": "Test Book",
        "authors": ["Author One"],
        "year": 2023,
        "publisher": "Test Publisher",
        "place": "Test City",
        "edition": 1
    }
    
    result = validate_citation_data(valid_data, mode="create")
    assert result is True

def test_validate_year_string_raises_exception():
    """Test that year as string raises exception."""
    invalid_data = {
        "type": "book",
        "title": "Test Book",
        "authors": ["Author One"],
        "year": "2023",
        "publisher": "Test Publisher",
        "place": "Test City",
        "edition": 1
    }
    
    with pytest.raises(HTTPException) as exc_info:
        validate_citation_data(invalid_data, mode="create")
    
    assert exc_info.value.status_code == 400
    assert "Year must be an integer or null" in exc_info.value.detail

def test_validate_year_future_or_negative_raises_exception():
    """Test that future or negative year raises exception."""
    invalid_data = {
        "type": "book",
        "title": "Test Book",
        "authors": ["Author One"],
        "year": 2030,  # Future year
        "publisher": "Test Publisher",
        "place": "Test City",
        "edition": 1
    }
    
    with pytest.raises(HTTPException) as exc_info:
        validate_citation_data(invalid_data, mode="create")
    
    assert exc_info.value.status_code == 400
    assert "Year must be a non-negative integer not exceeding" in exc_info.value.detail

def test_validate_title_valid_string_passes():
    """Test that valid title string passes validation."""
    valid_data = {
        "type": "book",
        "title": "Valid Title",
        "authors": ["Author One"],
        "year": 2023,
        "publisher": "Test Publisher",
        "place": "Test City",
        "edition": 1
    }
    
    result = validate_citation_data(valid_data, mode="create")
    assert result is True

def test_validate_title_empty_string_raises_exception():
    """Test that empty title raises exception."""
    invalid_data = {
        "type": "book",
        "title": "",
        "authors": ["Author One"],
        "year": 2023,
        "publisher": "Test Publisher",
        "place": "Test City",
        "edition": 1
    }
    
    with pytest.raises(HTTPException) as exc_info:
        validate_citation_data(invalid_data, mode="create")
    
    assert exc_info.value.status_code == 400
    assert "Title must be a non-empty string" in exc_info.value.detail

def test_validate_url_valid_format_passes():
    """Test that valid URL format passes validation."""
    valid_data = {
        "type": "website",
        "title": "Test Page",
        "authors": ["Author One"],
        "year": 2023,
        "publisher": "Test Publisher",
        "url": "https://example.com",
        "access_date": "2023-09-30"
    }
    
    result = validate_citation_data(valid_data, mode="create")
    assert result is True

def test_validate_url_invalid_format_raises_exception():
    """Test that invalid URL format raises exception."""
    invalid_data = {
        "type": "website",
        "title": "Test Page",
        "authors": ["Author One"],
        "year": 2023,
        "publisher": "Test Publisher",
        "url": "not-a-valid-url",
        "access_date": "2023-09-30"
    }
    
    with pytest.raises(HTTPException) as exc_info:
        validate_citation_data(invalid_data, mode="create")
    
    assert exc_info.value.status_code == 400
    assert "Invalid URL format" in exc_info.value.detail

def test_validate_doi_valid_format_passes():
    """Test that valid DOI format passes validation."""
    valid_data = {
        "type": "article",
        "title": "Test Article",
        "authors": ["Author One"],
        "year": 2023,
        "journal": "Test Journal",
        "volume": 1,
        "issue": "1",
        "pages": "1-10",
        "doi": "10.1234/test.2023"
    }
    
    result = validate_citation_data(valid_data, mode="create")
    assert result is True

def test_validate_doi_invalid_format_raises_exception():
    """Test that invalid DOI format raises exception."""
    invalid_data = {
        "type": "article",
        "title": "Test Article",
        "authors": ["Author One"],
        "year": 2023,
        "journal": "Test Journal",
        "volume": 1,
        "issue": "1",
        "pages": "1-10",
        "doi": "invalid-doi"
    }
    
    with pytest.raises(HTTPException) as exc_info:
        validate_citation_data(invalid_data, mode="create")
    
    assert exc_info.value.status_code == 400
    assert "Invalid DOI format (expected: 10.xxxx/xxxx)" in exc_info.value.detail

def test_validate_pages_valid_single_range_passes():
    """Test that valid single page range passes validation."""
    valid_data = {
        "type": "article",
        "title": "Test Article",
        "authors": ["Author One"],
        "year": 2023,
        "journal": "Test Journal",
        "volume": 1,
        "issue": "1",
        "pages": "1-10",
        "doi": "10.1234/test.2023"
    }
    
    result = validate_citation_data(valid_data, mode="create")
    assert result is True

def test_validate_pages_valid_multiple_ranges_passes():
    """Test that valid multiple page ranges pass validation."""
    valid_data = {
        "type": "article",
        "title": "Test Article",
        "authors": ["Author One"],
        "year": 2023,
        "journal": "Test Journal",
        "volume": 1,
        "issue": "1",
        "pages": "1-3, 5-7",
        "doi": "10.1234/test.2023"
    }
    
    result = validate_citation_data(valid_data, mode="create")
    assert result is True

def test_validate_pages_inverted_range_raises_exception():
    """Test that inverted page range raises exception."""
    invalid_data = {
        "type": "article",
        "title": "Test Article",
        "authors": ["Author One"],
        "year": 2023,
        "journal": "Test Journal",
        "volume": 1,
        "issue": "1",
        "pages": "10-1",  # Inverted range
        "doi": "10.1234/test.2023"
    }
    
    with pytest.raises(HTTPException) as exc_info:
        validate_citation_data(invalid_data, mode="create")
    
    assert exc_info.value.status_code == 400
    assert "Pages must be in format 'start-end'" in exc_info.value.detail

def test_validate_access_date_valid_format_passes():
    """Test that valid access date format passes validation."""
    valid_data = {
        "type": "website",
        "title": "Test Page",
        "authors": ["Author One"],
        "year": 2023,
        "publisher": "Test Publisher",
        "url": "https://example.com",
        "access_date": "2023-09-30"
    }
    
    result = validate_citation_data(valid_data, mode="create")
    assert result is True

def test_validate_access_date_invalid_format_raises_exception():
    """Test that invalid access date format raises exception."""
    invalid_data = {
        "type": "website",
        "title": "Test Page",
        "authors": ["Author One"],
        "year": 2023,
        "publisher": "Test Publisher",
        "url": "https://example.com",
        "access_date": "2023-02-30"  # Invalid date
    }
    
    with pytest.raises(HTTPException) as exc_info:
        validate_citation_data(invalid_data, mode="create")
    
    assert exc_info.value.status_code == 400
    assert "Access Date must be in YYYY-MM-DD format" in exc_info.value.detail

def test_validate_volume_valid_positive_integer_passes():
    """Test that valid positive volume integer passes validation."""
    valid_data = {
        "type": "article",
        "title": "Test Article",
        "authors": ["Author One"],
        "year": 2023,
        "journal": "Test Journal",
        "volume": 5,
        "issue": "1",
        "pages": "1-10",
        "doi": "10.1234/test.2023"
    }
    
    result = validate_citation_data(valid_data, mode="create")
    assert result is True

def test_validate_volume_zero_or_negative_raises_exception():
    """Test that zero or negative volume raises exception."""
    invalid_data = {
        "type": "article",
        "title": "Test Article",
        "authors": ["Author One"],
        "year": 2023,
        "journal": "Test Journal",
        "volume": 0,
        "issue": "1",
        "pages": "1-10",
        "doi": "10.1234/test.2023"
    }
    
    with pytest.raises(HTTPException) as exc_info:
        validate_citation_data(invalid_data, mode="create")
    
    assert exc_info.value.status_code == 400
    assert "Volume must be a positive integer" in exc_info.value.detail

def test_validate_edition_valid_positive_integer_passes():
    """Test that valid positive edition integer passes validation."""
    valid_data = {
        "type": "book",
        "title": "Test Book",
        "authors": ["Author One"],
        "year": 2023,
        "publisher": "Test Publisher",
        "place": "Test City",
        "edition": 2
    }
    
    result = validate_citation_data(valid_data, mode="create")
    assert result is True

def test_validate_edition_non_integer_raises_exception():
    """Test that non-integer edition raises exception."""
    invalid_data = {
        "type": "book",
        "title": "Test Book",
        "authors": ["Author One"],
        "year": 2023,
        "publisher": "Test Publisher",
        "place": "Test City",
        "edition": "second"
    }
    
    with pytest.raises(HTTPException) as exc_info:
        validate_citation_data(invalid_data, mode="create")
    
    assert exc_info.value.status_code == 400
    assert "Edition must be a positive integer" in exc_info.value.detail

def test_validate_issue_valid_string_passes():
    """Test that valid issue string passes validation."""
    valid_data = {
        "type": "article",
        "title": "Test Article",
        "authors": ["Author One"],
        "year": 2023,
        "journal": "Test Journal",
        "volume": 1,
        "issue": "Special Issue",
        "pages": "1-10",
        "doi": "10.1234/test.2023"
    }
    
    result = validate_citation_data(valid_data, mode="create")
    assert result is True

def test_validate_issue_empty_string_raises_exception():
    """Test that empty issue string raises exception."""
    invalid_data = {
        "type": "article",
        "title": "Test Article",
        "authors": ["Author One"],
        "year": 2023,
        "journal": "Test Journal",
        "volume": 1,
        "issue": "",
        "pages": "1-10",
        "doi": "10.1234/test.2023"
    }
    
    with pytest.raises(HTTPException) as exc_info:
        validate_citation_data(invalid_data, mode="create")
    
    assert exc_info.value.status_code == 400
    assert "Issue must be a non-empty string" in exc_info.value.detail

def test_validate_publisher_valid_string_passes():
    """Test that valid publisher string passes validation."""
    valid_data = {
        "type": "book",
        "title": "Test Book",
        "authors": ["Author One"],
        "year": 2023,
        "publisher": "Valid Publisher",
        "place": "Test City",
        "edition": 1
    }
    
    result = validate_citation_data(valid_data, mode="create")
    assert result is True

def test_validate_publisher_empty_string_raises_exception():
    """Test that empty publisher string raises exception."""
    invalid_data = {
        "type": "book",
        "title": "Test Book",
        "authors": ["Author One"],
        "year": 2023,
        "publisher": "",
        "place": "Test City",
        "edition": 1
    }
    
    with pytest.raises(HTTPException) as exc_info:
        validate_citation_data(invalid_data, mode="create")
    
    assert exc_info.value.status_code == 400
    assert "Publisher must be a non-empty string" in exc_info.value.detail

def test_validate_publisher_non_string_raises_exception():
    """Test that non-string publisher raises exception."""
    invalid_data = {
        "type": "book",
        "title": "Test Book",
        "authors": ["Author One"],
        "year": 2023,
        "publisher": 123,
        "place": "Test City",
        "edition": 1
    }
    
    with pytest.raises(HTTPException) as exc_info:
        validate_citation_data(invalid_data, mode="create")
    
    assert exc_info.value.status_code == 400
    assert "Publisher must be a non-empty string" in exc_info.value.detail

def test_validate_place_valid_string_passes():
    """Test that valid place string passes validation."""
    valid_data = {
        "type": "book",
        "title": "Test Book",
        "authors": ["Author One"],
        "year": 2023,
        "publisher": "Test Publisher",
        "place": "Valid City",
        "edition": 1
    }
    
    result = validate_citation_data(valid_data, mode="create")
    assert result is True

def test_validate_place_empty_string_raises_exception():
    """Test that empty place string raises exception."""
    invalid_data = {
        "type": "book",
        "title": "Test Book",
        "authors": ["Author One"],
        "year": 2023,
        "publisher": "Test Publisher",
        "place": "",
        "edition": 1
    }
    
    with pytest.raises(HTTPException) as exc_info:
        validate_citation_data(invalid_data, mode="create")
    
    assert exc_info.value.status_code == 400
    assert "Place must be a non-empty string" in exc_info.value.detail

def test_validate_place_non_string_raises_exception():
    """Test that non-string place raises exception."""
    invalid_data = {
        "type": "book",
        "title": "Test Book",
        "authors": ["Author One"],
        "year": 2023,
        "publisher": "Test Publisher",
        "place": None,
        "edition": 1
    }
    
    with pytest.raises(HTTPException) as exc_info:
        validate_citation_data(invalid_data, mode="create")
    
    assert exc_info.value.status_code == 400
    assert "Place must be a non-empty string" in exc_info.value.detail

def test_validate_journal_valid_string_passes():
    """Test that valid journal string passes validation."""
    valid_data = {
        "type": "article",
        "title": "Test Article",
        "authors": ["Author One"],
        "year": 2023,
        "journal": "Valid Journal",
        "volume": 1,
        "issue": "1",
        "pages": "1-10",
        "doi": "10.1234/test.2023"
    }
    
    result = validate_citation_data(valid_data, mode="create")
    assert result is True

def test_validate_journal_empty_string_raises_exception():
    """Test that empty journal string raises exception."""
    invalid_data = {
        "type": "article",
        "title": "Test Article",
        "authors": ["Author One"],
        "year": 2023,
        "journal": "",
        "volume": 1,
        "issue": "1",
        "pages": "1-10",
        "doi": "10.1234/test.2023"
    }
    
    with pytest.raises(HTTPException) as exc_info:
        validate_citation_data(invalid_data, mode="create")
    
    assert exc_info.value.status_code == 400
    assert "Journal must be a non-empty string" in exc_info.value.detail

def test_validate_journal_non_string_raises_exception():
    """Test that non-string journal raises exception."""
    invalid_data = {
        "type": "article",
        "title": "Test Article",
        "authors": ["Author One"],
        "year": 2023,
        "journal": 456,
        "volume": 1,
        "issue": "1",
        "pages": "1-10",
        "doi": "10.1234/test.2023"
    }
    
    with pytest.raises(HTTPException) as exc_info:
        validate_citation_data(invalid_data, mode="create")
    
    assert exc_info.value.status_code == 400
    assert "Journal must be a non-empty string" in exc_info.value.detail

def test_validate_year_none_passes():
    """Test that year as None passes validation."""
    valid_data = {
        "type": "book",
        "title": "Test Book",
        "authors": ["Author One"],
        "year": None,
        "publisher": "Test Publisher",
        "place": "Test City",
        "edition": 1
    }
    
    result = validate_citation_data(valid_data, mode="create")
    assert result is True

def test_validate_access_date_wrong_format_raises_exception():
    """Test that access date with wrong format raises exception."""
    invalid_data = {
        "type": "website",
        "title": "Test Page",
        "authors": ["Author One"],
        "year": 2023,
        "publisher": "Test Publisher",
        "url": "https://example.com",
        "access_date": "2023/01/01"  # Wrong format (should be YYYY-MM-DD)
    }
    
    with pytest.raises(HTTPException) as exc_info:
        validate_citation_data(invalid_data, mode="create")
    
    assert exc_info.value.status_code == 400
    assert "Access Date must be in YYYY-MM-DD format" in exc_info.value.detail

# ========== CHARACTER VALIDATION TESTS ==========

def test_validate_authors_valid_names_with_accents_passes():
    """Test that author names with accents and valid characters pass validation."""
    valid_data = {
        "type": "book",
        "title": "Test Book",
        "authors": ["María García-López", "Jean-Pierre O'Connor", "José María de la Cruz"],
        "year": 2023,
        "publisher": "Test Publisher",
        "place": "Test City",
        "edition": 1
    }
    
    result = validate_citation_data(valid_data, mode="create")
    assert result is True

def test_validate_authors_with_numbers_raises_exception():
    """Test that author names containing numbers raise exception."""
    invalid_data = {
        "type": "book",
        "title": "Test Book",
        "authors": ["John Smith", "Jane123 Doe"],
        "year": 2023,
        "publisher": "Test Publisher",
        "place": "Test City",
        "edition": 1
    }
    
    with pytest.raises(HTTPException) as exc_info:
        validate_citation_data(invalid_data, mode="create")
    
    assert exc_info.value.status_code == 400
    assert "Author names can only contain letters, spaces, hyphens, apostrophes, and periods" in exc_info.value.detail

def test_validate_authors_with_special_characters_raises_exception():
    """Test that author names containing special characters raise exception."""
    invalid_data = {
        "type": "book",
        "title": "Test Book",
        "authors": ["John Smith", "Jane@Doe"],
        "year": 2023,
        "publisher": "Test Publisher",
        "place": "Test City",
        "edition": 1
    }
    
    with pytest.raises(HTTPException) as exc_info:
        validate_citation_data(invalid_data, mode="create")
    
    assert exc_info.value.status_code == 400
    assert "Author names can only contain letters, spaces, hyphens, apostrophes, and periods" in exc_info.value.detail

def test_validate_authors_with_underscore_raises_exception():
    """Test that author names containing underscores raise exception."""
    invalid_data = {
        "type": "book",
        "title": "Test Book",
        "authors": ["John_Smith", "Jane Doe"],
        "year": 2023,
        "publisher": "Test Publisher",
        "place": "Test City",
        "edition": 1
    }
    
    with pytest.raises(HTTPException) as exc_info:
        validate_citation_data(invalid_data, mode="create")
    
    assert exc_info.value.status_code == 400
    assert "Author names can only contain letters, spaces, hyphens, apostrophes, and periods" in exc_info.value.detail

def test_validate_authors_with_hash_symbol_raises_exception():
    """Test that author names containing hash symbols raise exception."""
    invalid_data = {
        "type": "book",
        "title": "Test Book",
        "authors": ["John Smith", "Jane#Doe"],
        "year": 2023,
        "publisher": "Test Publisher",
        "place": "Test City",
        "edition": 1
    }
    
    with pytest.raises(HTTPException) as exc_info:
        validate_citation_data(invalid_data, mode="create")
    
    assert exc_info.value.status_code == 400
    assert "Author names can only contain letters, spaces, hyphens, apostrophes, and periods" in exc_info.value.detail

def test_validate_place_valid_names_with_accents_passes():
    """Test that place names with accents and valid characters pass validation."""
    valid_data = {
        "type": "book",
        "title": "Test Book",
        "authors": ["Author One"],
        "year": 2023,
        "publisher": "Test Publisher",
        "place": "São Paulo, Brazil",
        "edition": 1
    }
    
    result = validate_citation_data(valid_data, mode="create")
    assert result is True

def test_validate_place_with_hyphens_and_apostrophes_passes():
    """Test that place names with hyphens and apostrophes pass validation."""
    valid_data = {
        "type": "book",
        "title": "Test Book",
        "authors": ["Author One"],
        "year": 2023,
        "publisher": "Test Publisher",
        "place": "Saint-Denis, L'Île-de-France",
        "edition": 1
    }
    
    result = validate_citation_data(valid_data, mode="create")
    assert result is True

def test_validate_place_with_numbers_raises_exception():
    """Test that place names containing numbers raise exception."""
    invalid_data = {
        "type": "book",
        "title": "Test Book",
        "authors": ["Author One"],
        "year": 2023,
        "publisher": "Test Publisher",
        "place": "New York 123",
        "edition": 1
    }
    
    with pytest.raises(HTTPException) as exc_info:
        validate_citation_data(invalid_data, mode="create")
    
    assert exc_info.value.status_code == 400
    assert "Place names can only contain letters, spaces, hyphens, apostrophes, periods, and commas" in exc_info.value.detail

def test_validate_place_with_special_characters_raises_exception():
    """Test that place names containing special characters raise exception."""
    invalid_data = {
        "type": "book",
        "title": "Test Book",
        "authors": ["Author One"],
        "year": 2023,
        "publisher": "Test Publisher",
        "place": "New York@City",
        "edition": 1
    }
    
    with pytest.raises(HTTPException) as exc_info:
        validate_citation_data(invalid_data, mode="create")
    
    assert exc_info.value.status_code == 400
    assert "Place names can only contain letters, spaces, hyphens, apostrophes, periods, and commas" in exc_info.value.detail

def test_validate_place_with_hash_symbol_raises_exception():
    """Test that place names containing hash symbols raise exception."""
    invalid_data = {
        "type": "book",
        "title": "Test Book",
        "authors": ["Author One"],
        "year": 2023,
        "publisher": "Test Publisher",
        "place": "City#1",
        "edition": 1
    }
    
    with pytest.raises(HTTPException) as exc_info:
        validate_citation_data(invalid_data, mode="create")
    
    assert exc_info.value.status_code == 400
    assert "Place names can only contain letters, spaces, hyphens, apostrophes, periods, and commas" in exc_info.value.detail

def test_validate_place_with_dollar_sign_raises_exception():
    """Test that place names containing dollar signs raise exception."""
    invalid_data = {
        "type": "book",
        "title": "Test Book",
        "authors": ["Author One"],
        "year": 2023,
        "publisher": "Test Publisher",
        "place": "City$Name",
        "edition": 1
    }
    
    with pytest.raises(HTTPException) as exc_info:
        validate_citation_data(invalid_data, mode="create")
    
    assert exc_info.value.status_code == 400
    assert "Place names can only contain letters, spaces, hyphens, apostrophes, periods, and commas" in exc_info.value.detail

def test_validate_authors_multiple_invalid_characters_raises_exception():
    """Test that author names with multiple types of invalid characters raise exception."""
    invalid_data = {
        "type": "book",
        "title": "Test Book",
        "authors": ["John Smith", "Jane123@Doe#Test"],
        "year": 2023,
        "publisher": "Test Publisher",
        "place": "Test City",
        "edition": 1
    }
    
    with pytest.raises(HTTPException) as exc_info:
        validate_citation_data(invalid_data, mode="create")
    
    assert exc_info.value.status_code == 400
    assert "Author names can only contain letters, spaces, hyphens, apostrophes, and periods" in exc_info.value.detail

def test_validate_place_multiple_invalid_characters_raises_exception():
    """Test that place names with multiple types of invalid characters raise exception."""
    invalid_data = {
        "type": "book",
        "title": "Test Book",
        "authors": ["Author One"],
        "year": 2023,
        "publisher": "Test Publisher",
        "place": "City123@Name#Test",
        "edition": 1
    }
    
    with pytest.raises(HTTPException) as exc_info:
        validate_citation_data(invalid_data, mode="create")
    
    assert exc_info.value.status_code == 400
    assert "Place names can only contain letters, spaces, hyphens, apostrophes, periods, and commas" in exc_info.value.detail

# ========== LENGTH VALIDATION TESTS ==========

def test_validate_title_too_long_raises_exception():
    """Test that title exceeding maximum length raises exception."""
    long_title = "T" * 501  # MAX_TITLE_LENGTH is 500
    invalid_data = {
        "type": "book",
        "title": long_title,
        "authors": ["Author One"],
        "year": 2023,
        "publisher": "Test Publisher",
        "place": "Test City",
        "edition": 1
    }
    
    with pytest.raises(HTTPException) as exc_info:
        validate_citation_data(invalid_data, mode="create")
    
    assert exc_info.value.status_code == 400
    assert "Title exceeds maximum length of 500 characters" in exc_info.value.detail

def test_validate_title_at_maximum_length_passes():
    """Test that title at exactly maximum length passes validation."""
    max_title = "T" * 500  # MAX_TITLE_LENGTH is 500
    valid_data = {
        "type": "book",
        "title": max_title,
        "authors": ["Author One"],
        "year": 2023,
        "publisher": "Test Publisher",
        "place": "Test City",
        "edition": 1
    }
    
    # Should not raise exception
    result = validate_citation_data(valid_data, mode="create")
    assert result is True

def test_validate_author_name_too_long_raises_exception():
    """Test that author name exceeding maximum length raises exception."""
    long_author = "A" * 151  # MAX_AUTHOR_NAME_LENGTH is 150
    invalid_data = {
        "type": "book",
        "title": "Test Book",
        "authors": [long_author],
        "year": 2023,
        "publisher": "Test Publisher",
        "place": "Test City",
        "edition": 1
    }
    
    with pytest.raises(HTTPException) as exc_info:
        validate_citation_data(invalid_data, mode="create")
    
    assert exc_info.value.status_code == 400
    assert "Author name exceeds maximum length of 150 characters" in exc_info.value.detail

def test_validate_author_name_at_maximum_length_passes():
    """Test that author name at exactly maximum length passes validation."""
    max_author = "A" * 150  # MAX_AUTHOR_NAME_LENGTH is 150
    valid_data = {
        "type": "book",
        "title": "Test Book",
        "authors": [max_author],
        "year": 2023,
        "publisher": "Test Publisher",
        "place": "Test City",
        "edition": 1
    }
    
    # Should not raise exception
    result = validate_citation_data(valid_data, mode="create")
    assert result is True

def test_validate_publisher_too_long_raises_exception():
    """Test that publisher exceeding maximum length raises exception."""
    long_publisher = "P" * 201  # MAX_PUBLISHER_LENGTH is 200
    invalid_data = {
        "type": "book",
        "title": "Test Book",
        "authors": ["Author One"],
        "year": 2023,
        "publisher": long_publisher,
        "place": "Test City",
        "edition": 1
    }
    
    with pytest.raises(HTTPException) as exc_info:
        validate_citation_data(invalid_data, mode="create")
    
    assert exc_info.value.status_code == 400
    assert "Publisher exceeds maximum length of 200 characters" in exc_info.value.detail

def test_validate_publisher_at_maximum_length_passes():
    """Test that publisher at exactly maximum length passes validation."""
    max_publisher = "P" * 200  # MAX_PUBLISHER_LENGTH is 200
    valid_data = {
        "type": "book",
        "title": "Test Book",
        "authors": ["Author One"],
        "year": 2023,
        "publisher": max_publisher,
        "place": "Test City",
        "edition": 1
    }
    
    # Should not raise exception
    result = validate_citation_data(valid_data, mode="create")
    assert result is True

def test_validate_journal_too_long_raises_exception():
    """Test that journal exceeding maximum length raises exception."""
    long_journal = "J" * 201  # MAX_JOURNAL_LENGTH is 200
    invalid_data = {
        "type": "article",
        "title": "Test Article",
        "authors": ["Author One"],
        "year": 2023,
        "journal": long_journal,
        "volume": 1,
        "issue": "1",
        "pages": "1-10",
        "doi": "10.1234/test.2023"
    }
    
    with pytest.raises(HTTPException) as exc_info:
        validate_citation_data(invalid_data, mode="create")
    
    assert exc_info.value.status_code == 400
    assert "Journal exceeds maximum length of 200 characters" in exc_info.value.detail

def test_validate_journal_at_maximum_length_passes():
    """Test that journal at exactly maximum length passes validation."""
    max_journal = "J" * 200  # MAX_JOURNAL_LENGTH is 200
    valid_data = {
        "type": "article",
        "title": "Test Article",
        "authors": ["Author One"],
        "year": 2023,
        "journal": max_journal,
        "volume": 1,
        "issue": "1",
        "pages": "1-10",
        "doi": "10.1234/test.2023"
    }
    
    # Should not raise exception
    result = validate_citation_data(valid_data, mode="create")
    assert result is True

def test_validate_place_too_long_raises_exception():
    """Test that place exceeding maximum length raises exception."""
    long_place = "P" * 101  # MAX_PLACE_LENGTH is 100
    invalid_data = {
        "type": "book",
        "title": "Test Book",
        "authors": ["Author One"],
        "year": 2023,
        "publisher": "Test Publisher",
        "place": long_place,
        "edition": 1
    }
    
    with pytest.raises(HTTPException) as exc_info:
        validate_citation_data(invalid_data, mode="create")
    
    assert exc_info.value.status_code == 400
    assert "Place exceeds maximum length of 100 characters" in exc_info.value.detail

def test_validate_place_at_maximum_length_passes():
    """Test that place at exactly maximum length passes validation."""
    max_place = "P" * 100  # MAX_PLACE_LENGTH is 100
    valid_data = {
        "type": "book",
        "title": "Test Book",
        "authors": ["Author One"],
        "year": 2023,
        "publisher": "Test Publisher",
        "place": max_place,
        "edition": 1
    }
    
    # Should not raise exception
    result = validate_citation_data(valid_data, mode="create")
    assert result is True

def test_validate_url_too_long_raises_exception():
    """Test that URL exceeding maximum length raises exception."""
    # Create a valid URL that exceeds MAX_URL_LENGTH (2000)
    long_url = "https://example.com/" + "a" * 1981  # Total = 2001 chars (exceeds limit)
    invalid_data = {
        "type": "website",
        "title": "Test Website",
        "authors": ["Author One"],
        "year": 2023,
        "publisher": "Test Publisher",
        "url": long_url,
        "access_date": "2023-01-01"
    }
    
    with pytest.raises(HTTPException) as exc_info:
        validate_citation_data(invalid_data, mode="create")
    
    assert exc_info.value.status_code == 400
    assert "URL exceeds maximum length of 2000 characters" in exc_info.value.detail

def test_validate_url_at_maximum_length_passes():
    """Test that URL at exactly maximum length passes validation."""
    # Create a valid URL that is exactly MAX_URL_LENGTH (2000)
    max_url = "https://example.com/" + "a" * 1980  # Total = 2000 chars exactly
    valid_data = {
        "type": "website",
        "title": "Test Website",
        "authors": ["Author One"],
        "year": 2023,
        "publisher": "Test Publisher",
        "url": max_url,
        "access_date": "2023-01-01"
    }
    
    # Should not raise exception
    result = validate_citation_data(valid_data, mode="create")
    assert result is True

def test_validate_doi_too_long_raises_exception():
    """Test that DOI exceeding maximum length raises exception."""
    # Create a valid DOI that exceeds MAX_DOI_LENGTH (300)
    long_doi = "10.1234/" + "a" * 293  # Total = 301 chars (exceeds limit)
    invalid_data = {
        "type": "article",
        "title": "Test Article",
        "authors": ["Author One"],
        "year": 2023,
        "journal": "Test Journal",
        "volume": 1,
        "issue": "1",
        "pages": "1-10",
        "doi": long_doi
    }
    
    with pytest.raises(HTTPException) as exc_info:
        validate_citation_data(invalid_data, mode="create")
    
    assert exc_info.value.status_code == 400
    assert "DOI exceeds maximum length of 300 characters" in exc_info.value.detail

def test_validate_doi_at_maximum_length_passes():
    """Test that DOI at exactly maximum length passes validation."""
    # Create a valid DOI that is exactly MAX_DOI_LENGTH (300)
    max_doi = "10.1234/" + "a" * 291  # Total = 300 chars
    valid_data = {
        "type": "article",
        "title": "Test Article",
        "authors": ["Author One"],
        "year": 2023,
        "journal": "Test Journal",
        "volume": 1,
        "issue": "1",
        "pages": "1-10",
        "doi": max_doi
    }
    
    # Should not raise exception
    result = validate_citation_data(valid_data, mode="create")
    assert result is True

def test_validate_pages_too_long_raises_exception():
    """Test that pages exceeding maximum length raises exception."""
    long_pages = "1-" + "9" * 49  # Total = 51 chars (exceeds MAX_PAGES_LENGTH of 50)
    invalid_data = {
        "type": "article",
        "title": "Test Article",
        "authors": ["Author One"],
        "year": 2023,
        "journal": "Test Journal",
        "volume": 1,
        "issue": "1",
        "pages": long_pages,
        "doi": "10.1234/test.2023"
    }
    
    with pytest.raises(HTTPException) as exc_info:
        validate_citation_data(invalid_data, mode="create")
    
    assert exc_info.value.status_code == 400
    assert "Pages exceeds maximum length of 50 characters" in exc_info.value.detail

def test_validate_pages_at_maximum_length_passes():
    """Test that pages at exactly maximum length passes validation."""
    # Create pages that are exactly MAX_PAGES_LENGTH (50)
    max_pages = "1-" + "9" * 47  # Total = 50 chars
    valid_data = {
        "type": "article",
        "title": "Test Article",
        "authors": ["Author One"],
        "year": 2023,
        "journal": "Test Journal",
        "volume": 1,
        "issue": "1",
        "pages": max_pages,
        "doi": "10.1234/test.2023"
    }
    
    # Should not raise exception
    result = validate_citation_data(valid_data, mode="create")
    assert result is True

def test_validate_issue_too_long_raises_exception():
    """Test that issue exceeding maximum length raises exception."""
    long_issue = "I" * 51  # MAX_ISSUE_LENGTH is 50
    invalid_data = {
        "type": "article",
        "title": "Test Article",
        "authors": ["Author One"],
        "year": 2023,
        "journal": "Test Journal",
        "volume": 1,
        "issue": long_issue,
        "pages": "1-10",
        "doi": "10.1234/test.2023"
    }
    
    with pytest.raises(HTTPException) as exc_info:
        validate_citation_data(invalid_data, mode="create")
    
    assert exc_info.value.status_code == 400
    assert "Issue exceeds maximum length of 50 characters" in exc_info.value.detail

def test_validate_issue_at_maximum_length_passes():
    """Test that issue at exactly maximum length passes validation."""
    max_issue = "I" * 50  # MAX_ISSUE_LENGTH is 50
    valid_data = {
        "type": "article",
        "title": "Test Article",
        "authors": ["Author One"],
        "year": 2023,
        "journal": "Test Journal",
        "volume": 1,
        "issue": max_issue,
        "pages": "1-10",
        "doi": "10.1234/test.2023"
    }
    
    # Should not raise exception
    result = validate_citation_data(valid_data, mode="create")
    assert result is True

def test_validate_multiple_length_violations_raises_exception():
    """Test that multiple length violations show the first violation encountered."""
    long_title = "T" * 501  # Exceeds title limit
    long_author = "A" * 151  # Exceeds author limit
    invalid_data = {
        "type": "book",
        "title": long_title,
        "authors": [long_author],
        "year": 2023,
        "publisher": "Test Publisher",
        "place": "Test City",
        "edition": 1
    }
    
    with pytest.raises(HTTPException) as exc_info:
        validate_citation_data(invalid_data, mode="create")
    
    assert exc_info.value.status_code == 400
    # Should show the first length violation encountered (title)
    assert "Title exceeds maximum length of 500 characters" in exc_info.value.detail

def test_validate_length_with_whitespace_trimming():
    """Test that length validation considers trimmed values."""
    # Title with whitespace that becomes valid after trimming
    title_with_spaces = "   " + "T" * 495 + "   "  # 501 total, but 495 after trim (valid)
    valid_data = {
        "type": "book",
        "title": title_with_spaces,
        "authors": ["Author One"],
        "year": 2023,
        "publisher": "Test Publisher",
        "place": "Test City",
        "edition": 1
    }
    
    # Should not raise exception because trimmed title is 495 chars (valid)
    result = validate_citation_data(valid_data, mode="create")
    assert result is True
