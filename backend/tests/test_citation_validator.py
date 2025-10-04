# backend/tests/test_citation_validator.py
import pytest
from fastapi import HTTPException
from services.validators.citation_validator import validate_citation_data

# Test cases for validate_citation_data general functionality

def test_validate_citation_data_supported_type_passes():
    """Test that supported citation types pass validation."""
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

# Test cases for field format validations

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

# Test cases for new character validation in authors and place fields

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
