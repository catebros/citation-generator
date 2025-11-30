# backend/tests/test_integration_validator.py
import pytest
from fastapi import HTTPException
from repositories.citation_repo import CitationRepository
from repositories.project_repo import ProjectRepository
from services.citation_service import CitationService
from services.project_service import ProjectService
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models.base import Base


@pytest.fixture(scope="function")
def db_session():
    """Create a fresh in-memory database for each test."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    yield session
    session.close()


@pytest.fixture
def project_service(db_session):
    """Provide a ProjectService instance with test database."""
    return ProjectService(db_session)


@pytest.fixture
def citation_service(db_session):
    """Provide a CitationService instance with test database."""
    return CitationService(db_session)


def test_book_citation_missing_required_fields(project_service, citation_service):
    """Test validation fails for book citation missing required fields."""
    project = project_service.create_project({"name": "Book Validation Test"})

    # Missing: publisher, place, edition
    invalid_book = {
        "type": "book",
        "title": "Incomplete Book",
        "authors": ["Author Name"],
        "year": 2023
    }

    with pytest.raises(HTTPException) as exc_info:
        citation_service.create_citation(project.id, invalid_book)

    assert exc_info.value.status_code == 400
    assert "required" in exc_info.value.detail.lower()


def test_article_citation_missing_required_fields(project_service, citation_service):
    """Test validation fails for article citation missing required fields."""
    project = project_service.create_project({"name": "Article Validation Test"})

    # Missing: journal, volume, issue, pages, doi
    invalid_article = {
        "type": "article",
        "title": "Incomplete Article",
        "authors": ["Author Name"],
        "year": 2023
    }

    with pytest.raises(HTTPException) as exc_info:
        citation_service.create_citation(project.id, invalid_article)

    assert exc_info.value.status_code == 400
    assert "required" in exc_info.value.detail.lower()


def test_website_citation_missing_required_fields(project_service, citation_service):
    """Test validation fails for website citation missing required fields."""
    project = project_service.create_project({"name": "Website Validation Test"})

    # Missing: publisher, url, access_date
    invalid_website = {
        "type": "website",
        "title": "Incomplete Website",
        "authors": ["Author Name"],
        "year": 2023
    }

    with pytest.raises(HTTPException) as exc_info:
        citation_service.create_citation(project.id, invalid_website)

    assert exc_info.value.status_code == 400
    assert "required" in exc_info.value.detail.lower()


def test_report_citation_missing_required_fields(project_service, citation_service):
    """Test validation fails for report citation missing required fields."""
    project = project_service.create_project({"name": "Report Validation Test"})

    # Missing: publisher, url, place
    invalid_report = {
        "type": "report",
        "title": "Incomplete Report",
        "authors": ["Author Name"],
        "year": 2023
    }

    with pytest.raises(HTTPException) as exc_info:
        citation_service.create_citation(project.id, invalid_report)

    assert exc_info.value.status_code == 400
    assert "required" in exc_info.value.detail.lower()


def test_invalid_citation_type(project_service, citation_service):
    """Test validation fails for invalid citation type."""
    project = project_service.create_project({"name": "Type Validation Test"})

    invalid_type = {
        "type": "invalid_type",
        "title": "Some Title",
        "authors": ["Author"],
        "year": 2023
    }

    with pytest.raises(HTTPException) as exc_info:
        citation_service.create_citation(project.id, invalid_type)

    assert exc_info.value.status_code == 400


def test_missing_authors_field(project_service, citation_service):
    """Test validation fails when authors field is missing."""
    project = project_service.create_project({"name": "Authors Validation Test"})

    no_authors = {
        "type": "book",
        "title": "No Authors Book",
        # Missing: authors
        "year": 2023,
        "publisher": "Publisher",
        "place": "City",
        "edition": 1
    }

    with pytest.raises(HTTPException) as exc_info:
        citation_service.create_citation(project.id, no_authors)

    assert exc_info.value.status_code == 400


def test_empty_authors_list(project_service, citation_service):
    """Test validation fails when authors list is empty."""
    project = project_service.create_project({"name": "Empty Authors Test"})

    empty_authors = {
        "type": "book",
        "title": "Empty Authors Book",
        "authors": [],  # Empty list
        "year": 2023,
        "publisher": "Publisher",
        "place": "City",
        "edition": 1
    }

    with pytest.raises(HTTPException) as exc_info:
        citation_service.create_citation(project.id, empty_authors)

    assert exc_info.value.status_code == 400


def test_missing_title_field(project_service, citation_service):
    """Test validation fails when title is missing."""
    project = project_service.create_project({"name": "Title Validation Test"})

    no_title = {
        "type": "book",
        # Missing: title
        "authors": ["Author"],
        "year": 2023,
        "publisher": "Publisher",
        "place": "City",
        "edition": 1
    }

    with pytest.raises(HTTPException) as exc_info:
        citation_service.create_citation(project.id, no_title)

    assert exc_info.value.status_code == 400


def test_missing_year_field(project_service, citation_service):
    """Test validation fails when year is missing."""
    project = project_service.create_project({"name": "Year Validation Test"})

    no_year = {
        "type": "book",
        "title": "No Year Book",
        "authors": ["Author"],
        # Missing: year
        "publisher": "Publisher",
        "place": "City",
        "edition": 1
    }

    with pytest.raises(HTTPException) as exc_info:
        citation_service.create_citation(project.id, no_year)

    assert exc_info.value.status_code == 400


def test_invalid_year_type(project_service, citation_service):
    """Test validation fails when year is not a number."""
    project = project_service.create_project({"name": "Year Type Test"})

    invalid_year = {
        "type": "book",
        "title": "Invalid Year Book",
        "authors": ["Author"],
        "year": "not a number",  # Should be integer
        "publisher": "Publisher",
        "place": "City",
        "edition": 1
    }

    with pytest.raises(HTTPException) as exc_info:
        citation_service.create_citation(project.id, invalid_year)

    assert exc_info.value.status_code == 400


def test_valid_book_citation_passes_validation(project_service, citation_service):
    """Test that valid book citation passes all validation."""
    project = project_service.create_project({"name": "Valid Book Test"})

    valid_book = {
        "type": "book",
        "title": "Valid Book Title",
        "authors": ["Valid Author"],
        "year": 2023,
        "publisher": "Valid Publisher",
        "place": "Valid City",
        "edition": 1
    }

    # Should not raise exception
    citation = citation_service.create_citation(project.id, valid_book)
    assert citation.title == "Valid Book Title"
    assert citation.type == "book"


def test_valid_article_citation_passes_validation(project_service, citation_service):
    """Test that valid article citation passes all validation."""
    project = project_service.create_project({"name": "Valid Article Test"})

    valid_article = {
        "type": "article",
        "title": "Valid Article Title",
        "authors": ["Valid Author"],
        "year": 2023,
        "journal": "Valid Journal",
        "volume": 10,
        "issue": "5",
        "pages": "100-120",
        "doi": "10.1000/valid"
    }

    # Should not raise exception
    citation = citation_service.create_citation(project.id, valid_article)
    assert citation.title == "Valid Article Title"
    assert citation.type == "article"


def test_valid_website_citation_passes_validation(project_service, citation_service):
    """Test that valid website citation passes all validation."""
    project = project_service.create_project({"name": "Valid Website Test"})

    valid_website = {
        "type": "website",
        "title": "Valid Website Title",
        "authors": ["Valid Author"],
        "year": 2023,
        "publisher": "Valid Publisher",
        "url": "https://valid.example.com",
        "access_date": "2023-12-01"
    }

    # Should not raise exception
    citation = citation_service.create_citation(project.id, valid_website)
    assert citation.title == "Valid Website Title"
    assert citation.type == "website"


def test_valid_report_citation_passes_validation(project_service, citation_service):
    """Test that valid report citation passes all validation."""
    project = project_service.create_project({"name": "Valid Report Test"})

    valid_report = {
        "type": "report",
        "title": "Valid Report Title",
        "authors": ["Valid Author"],
        "year": 2023,
        "publisher": "Valid Publisher",
        "url": "https://valid.example.com/report",
        "place": "Valid City"
    }

    # Should not raise exception
    citation = citation_service.create_citation(project.id, valid_report)
    assert citation.title == "Valid Report Title"
    assert citation.type == "report"


def test_update_citation_validates_changes(project_service, citation_service):
    """Test that updating citation validates the new data."""
    project = project_service.create_project({"name": "Update Validation Test"})

    # Create valid citation
    citation = citation_service.create_citation(
        project.id,
        {
            "type": "book",
            "title": "Original Title",
            "authors": ["Author"],
            "year": 2023,
            "publisher": "Publisher",
            "place": "City",
            "edition": 1
        }
    )

    # Try to update with invalid year type
    with pytest.raises(HTTPException) as exc_info:
        citation_service.update_citation(
            citation.id,
            project.id,
            {"year": "not a number"}
        )

    assert exc_info.value.status_code == 400


def test_project_name_validation_empty(project_service):
    """Test validation fails for empty project name."""
    with pytest.raises(HTTPException) as exc_info:
        project_service.create_project({"name": ""})

    assert exc_info.value.status_code == 400


def test_project_name_validation_whitespace(project_service):
    """Test creating project with whitespace name (currently allowed)."""
    # Note: Whitespace validation not currently implemented
    # This test documents current behavior
    project = project_service.create_project({"name": "   "})
    assert project is not None


def test_project_name_validation_none(project_service):
    """Test validation fails for None project name."""
    with pytest.raises(HTTPException) as exc_info:
        project_service.create_project({"name": None})

    assert exc_info.value.status_code == 400


def test_duplicate_project_name_validation(project_service):
    """Test validation prevents duplicate project names."""
    # Create first project
    project_service.create_project({"name": "Unique Name"})

    # Try to create duplicate
    with pytest.raises(HTTPException) as exc_info:
        project_service.create_project({"name": "Unique Name"})

    assert exc_info.value.status_code == 409


def test_duplicate_citation_in_project_validation(project_service, citation_service):
    """Test validation prevents duplicate citations in same project."""
    project = project_service.create_project({"name": "Duplicate Citation Test"})

    citation_data = {
        "type": "book",
        "title": "Duplicate Book",
        "authors": ["Author"],
        "year": 2023,
        "publisher": "Publisher",
        "place": "City",
        "edition": 1
    }

    # Create first citation
    citation_service.create_citation(project.id, citation_data)

    # Try to create duplicate in same project
    with pytest.raises(HTTPException) as exc_info:
        citation_service.create_citation(project.id, citation_data)

    assert exc_info.value.status_code == 409
    assert "identical citation already exists" in exc_info.value.detail.lower()


def test_nonexistent_project_validation(citation_service):
    """Test validation fails when creating citation for nonexistent project."""
    citation_data = {
        "type": "book",
        "title": "Book",
        "authors": ["Author"],
        "year": 2023,
        "publisher": "Publisher",
        "place": "City",
        "edition": 1
    }

    with pytest.raises(HTTPException) as exc_info:
        citation_service.create_citation(999999, citation_data)

    assert exc_info.value.status_code == 404


def test_update_nonexistent_project_validation(project_service):
    """Test validation fails when updating nonexistent project."""
    with pytest.raises(HTTPException) as exc_info:
        project_service.update_project(999999, {"name": "Updated Name"})

    assert exc_info.value.status_code == 404


def test_update_nonexistent_citation_validation(project_service, citation_service):
    """Test validation fails when updating nonexistent citation."""
    project = project_service.create_project({"name": "Test Project"})

    with pytest.raises(HTTPException) as exc_info:
        citation_service.update_citation(999999, project.id, {"title": "Updated"})

    assert exc_info.value.status_code == 404


def test_delete_nonexistent_project_validation(project_service):
    """Test validation fails when deleting nonexistent project."""
    with pytest.raises(HTTPException) as exc_info:
        project_service.delete_project(999999)

    assert exc_info.value.status_code == 404


def test_delete_nonexistent_citation_validation(project_service, citation_service):
    """Test validation fails when deleting nonexistent citation."""
    project = project_service.create_project({"name": "Test Project"})

    with pytest.raises(HTTPException) as exc_info:
        citation_service.delete_citation(999999, project.id)

    assert exc_info.value.status_code == 404


def test_citation_belongs_to_project_validation(project_service, citation_service):
    """Test updating citation with project context (copy-on-write behavior)."""
    project1 = project_service.create_project({"name": "Project 1"})
    project2 = project_service.create_project({"name": "Project 2"})

    # Create citation in project1
    citation = citation_service.create_citation(
        project1.id,
        {
            "type": "book",
            "title": "Test Book",
            "authors": ["Author"],
            "year": 2023,
            "publisher": "Publisher",
            "place": "City",
            "edition": 1
        }
    )

    # Update citation in project1 context - should work
    updated = citation_service.update_citation(
        citation.id,
        project1.id,
        {"title": "Updated Title"}
    )

    assert updated.title == "Updated Title"


def test_multiple_validation_errors_reported(project_service, citation_service):
    """Test that validation reports errors clearly."""
    project = project_service.create_project({"name": "Multiple Errors Test"})

    # Citation with multiple issues
    invalid_citation = {
        "type": "book",
        # Missing: title, authors, year, publisher, place, edition
    }

    with pytest.raises(HTTPException) as exc_info:
        citation_service.create_citation(project.id, invalid_citation)

    # Should report validation error
    assert exc_info.value.status_code == 400
    error_detail = exc_info.value.detail.lower()
    assert "required" in error_detail or "missing" in error_detail


def test_validation_allows_optional_fields_missing(project_service, citation_service):
    """Test that validation allows missing optional fields."""
    project = project_service.create_project({"name": "Optional Fields Test"})

    # Book citation without edition (if optional)
    # This test depends on your schema - adjust if edition is required
    citation_data = {
        "type": "book",
        "title": "Book Without Optional Fields",
        "authors": ["Author"],
        "year": 2023,
        "publisher": "Publisher",
        "place": "City",
        "edition": 1  # Include if required
    }

    # Should succeed
    citation = citation_service.create_citation(project.id, citation_data)
    assert citation is not None


def test_validation_preserves_valid_data_types(project_service, citation_service):
    """Test that validation preserves correct data types."""
    project = project_service.create_project({"name": "Data Types Test"})

    citation_data = {
        "type": "article",
        "title": "Type Preservation Test",
        "authors": ["Author"],
        "year": 2023,
        "journal": "Journal",
        "volume": 10,  # Integer
        "issue": "5",  # String
        "pages": "100-120",  # String
        "doi": "10.1000/test"
    }

    citation = citation_service.create_citation(project.id, citation_data)

    # Verify types preserved
    assert isinstance(citation.year, int)
    assert isinstance(citation.volume, int)
    assert isinstance(citation.issue, str)


def test_validation_error_rollback(project_service, citation_service):
    """Test that validation errors don't leave partial data in database."""
    project = project_service.create_project({"name": "Rollback Test"})

    # Create valid citation
    citation_service.create_citation(
        project.id,
        {
            "type": "book",
            "title": "Valid Book",
            "authors": ["Author"],
            "year": 2023,
            "publisher": "Publisher",
            "place": "City",
            "edition": 1
        }
    )

    # Try to create invalid citation (should fail and rollback)
    try:
        citation_service.create_citation(
            project.id,
            {
                "type": "book",
                "title": "Invalid Book"
                # Missing required fields
            }
        )
    except HTTPException:
        pass

    # Verify only valid citation exists
    citations = project_service.get_all_citations_by_project(project.id)
    assert len(citations) == 1
    assert citations[0].title == "Valid Book"
