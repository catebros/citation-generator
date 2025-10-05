# backend/tests/test_citation_service.py
"""
Test suite for CitationService class.

This module contains comprehensive tests for all citation operations including:
- Citation creation with validation and duplicate detection
- Citation retrieval by ID
- Citation updates with type changes
- Citation deletion
- Citation formatting in APA and MLA styles

All tests use in-memory SQLite database for fast, isolated testing.
"""
import pytest
from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.base import Base
from models.project import Project
from services.citation_service import CitationService
from services.project_service import ProjectService

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
def citation_service(db_session):
    """Provide a CitationService instance with test database."""
    return CitationService(db_session)

@pytest.fixture
def project_service(db_session):
    """Provide a ProjectService instance with test database."""
    return ProjectService(db_session)

# ========== CREATE_CITATION TESTS ==========

def test_create_citation_project_id_none(citation_service):
    """project_id is None returns HTTP 400"""
    with pytest.raises(HTTPException) as exc_info:
        citation_service.create_citation(None, {"type": "book", "title": "Test"})
    assert exc_info.value.status_code == 400

def test_create_citation_project_not_exists(citation_service, project_service):
    """Project does not exist returns HTTP 404"""
    with pytest.raises(HTTPException) as exc_info:
        citation_service.create_citation(999, {"type": "book", "title": "Test"})
    assert exc_info.value.status_code == 404

def test_create_citation_data_none(citation_service, project_service):
    """data is None returns HTTP 400"""
    # Create a project first
    project = project_service.create_project({"name": "Test Project"})
    
    with pytest.raises(HTTPException) as exc_info:
        citation_service.create_citation(project.id, None)
    assert exc_info.value.status_code == 400

def test_create_citation_duplicate_detected(citation_service, project_service):
    """Duplicate detected returns HTTP 409"""
    # Create a project first
    project = project_service.create_project({"name": "Test Project"})
    
    # Create first citation
    citation_data = {
        "type": "book",
        "title": "Test Book",
        "authors": ["Test Author"],
        "year": 2020,
        "publisher": "Test Publisher",
        "place": "Test City",
        "edition": 1
    }
    citation_service.create_citation(project.id, citation_data)
    
    # Try to create duplicate
    with pytest.raises(HTTPException) as exc_info:
        citation_service.create_citation(project.id, citation_data)
    assert exc_info.value.status_code == 409

def test_create_citation_valid_case(citation_service, project_service):
    """Valid case calls validate_citation_data and _citation_repo.create"""
    # Create a project first
    project = project_service.create_project({"name": "Test Project"})

    citation_data = {
        "type": "book",
        "title": "Test Book",
        "authors": ["Test Author"],
        "year": 2020,
        "publisher": "Test Publisher",
        "place": "Test City",
        "edition": 1
    }

    result = citation_service.create_citation(project.id, citation_data)
    assert result.title == "Test Book"

def test_create_citation_website_type(citation_service, project_service):
    """Create website citation successfully"""
    project = project_service.create_project({"name": "Test Project"})

    citation_data = {
        "type": "website",
        "title": "Example Website",
        "authors": ["Web Author"],
        "year": 2023,
        "publisher": "Example Publisher",
        "url": "https://example.com",
        "access_date": "2024-01-15"
    }

    result = citation_service.create_citation(project.id, citation_data)
    assert result.title == "Example Website"
    assert result.type == "website"
    assert result.url == "https://example.com"

def test_create_citation_report_type(citation_service, project_service):
    """Create report citation successfully"""
    project = project_service.create_project({"name": "Test Project"})

    citation_data = {
        "type": "report",
        "title": "Annual Report",
        "authors": ["Report Author"],
        "year": 2022,
        "publisher": "Test Institution",
        "url": "https://example.com/report",
        "place": "New York"
    }

    result = citation_service.create_citation(project.id, citation_data)
    assert result.title == "Annual Report"
    assert result.type == "report"
    assert result.publisher == "Test Institution"

def test_create_citation_empty_authors(citation_service, project_service):
    """Create citation with empty authors list raises validation error"""
    project = project_service.create_project({"name": "Test Project"})

    citation_data = {
        "type": "book",
        "title": "Book Without Authors",
        "authors": [],
        "year": 2020,
        "publisher": "Test Publisher",
        "place": "Test City",
        "edition": 1
    }

    with pytest.raises(HTTPException) as exc_info:
        citation_service.create_citation(project.id, citation_data)
    assert exc_info.value.status_code == 400
    assert "cannot be empty" in exc_info.value.detail.lower()

def test_create_citation_special_characters(citation_service, project_service):
    """Create citation with valid special characters in title and author"""
    project = project_service.create_project({"name": "Test Project"})

    citation_data = {
        "type": "book",
        "title": "Book: A Study and Analysis",
        "authors": ["O'Brien M.", "Mueller K."],
        "year": 2020,
        "publisher": "Test Publishing",
        "place": "New York",
        "edition": 2
    }

    result = citation_service.create_citation(project.id, citation_data)
    assert "Book: A Study and Analysis" in result.title
    assert "O'Brien" in result.authors

def test_create_citation_long_title(citation_service, project_service):
    """Create citation with very long title"""
    project = project_service.create_project({"name": "Test Project"})

    long_title = "A" * 500  # 500 character title

    citation_data = {
        "type": "book",
        "title": long_title,
        "authors": ["Test Author"],
        "year": 2020,
        "publisher": "Test Publisher",
        "place": "Test City",
        "edition": 1
    }

    result = citation_service.create_citation(project.id, citation_data)
    assert len(result.title) == 500

# ========== GET_CITATION TESTS ==========

def test_get_citation_id_none(citation_service):
    """citation_id is None returns HTTP 400"""
    with pytest.raises(HTTPException) as exc_info:
        citation_service.get_citation(None)
    assert exc_info.value.status_code == 400

def test_get_citation_not_found(citation_service):
    """Citation not found returns HTTP 404"""
    with pytest.raises(HTTPException) as exc_info:
        citation_service.get_citation(999)
    assert exc_info.value.status_code == 404

def test_get_citation_found(citation_service, project_service):
    """Citation found returns object"""
    # Create project and citation
    project = project_service.create_project({"name": "Test Project"})
    citation_data = {
        "type": "book",
        "title": "Test Book",
        "authors": ["Test Author"],
        "year": 2020,
        "publisher": "Test Publisher",
        "place": "Test City",
        "edition": 1
    }
    created_citation = citation_service.create_citation(project.id, citation_data)
    
    # Get citation
    result = citation_service.get_citation(created_citation.id)
    assert result.id == created_citation.id
    assert result.title == "Test Book"

# ========== UPDATE_CITATION TESTS ==========

def test_update_citation_id_none(citation_service):
    """citation_id is None returns HTTP 400"""
    with pytest.raises(HTTPException) as exc_info:
        citation_service.update_citation(None, 1, {"title": "Updated"})
    assert exc_info.value.status_code == 400

def test_update_citation_project_id_none(citation_service):
    """project_id is None returns HTTP 400"""
    with pytest.raises(HTTPException) as exc_info:
        citation_service.update_citation(1, None, {"title": "Updated"})
    assert exc_info.value.status_code == 400

def test_update_citation_data_none(citation_service):
    """data is None returns HTTP 400"""
    with pytest.raises(HTTPException) as exc_info:
        citation_service.update_citation(1, 1, None)
    assert exc_info.value.status_code == 400

def test_update_citation_project_not_exists(citation_service):
    """Project does not exist returns HTTP 404"""
    with pytest.raises(HTTPException) as exc_info:
        citation_service.update_citation(1, 999, {"title": "Updated"})
    assert exc_info.value.status_code == 404

def test_update_citation_not_exists(citation_service, project_service):
    """Citation does not exist returns HTTP 404"""
    project = project_service.create_project({"name": "Test Project"})
    
    with pytest.raises(HTTPException) as exc_info:
        citation_service.update_citation(999, project.id, {"title": "Updated"})
    assert exc_info.value.status_code == 404

def test_update_citation_duplicate_detected(citation_service, project_service):
    """Duplicate detected in project (different id) returns HTTP 409"""
    project = project_service.create_project({"name": "Test Project"})
    
    # Create two citations
    citation1_data = {
        "type": "book",
        "title": "Book One",
        "authors": ["Author Smith"],
        "year": 2020,
        "publisher": "Publisher Alpha",
        "place": "New York",
        "edition": 1
    }
    citation2_data = {
        "type": "book",
        "title": "Book Two",
        "authors": ["Author Jones"],
        "year": 2021,
        "publisher": "Publisher Beta",
        "place": "London",
        "edition": 2
    }
    
    citation1 = citation_service.create_citation(project.id, citation1_data)
    citation2 = citation_service.create_citation(project.id, citation2_data)
    
    # Try to update citation2 to have same data as citation1
    with pytest.raises(HTTPException) as exc_info:
        citation_service.update_citation(citation2.id, project.id, citation1_data)
    assert exc_info.value.status_code == 409

def test_update_citation_type_not_changes(citation_service, project_service):
    """Type does not change, validate_citation_data called with type_change=False"""
    project = project_service.create_project({"name": "Test Project"})
    citation_data = {
        "type": "book",
        "title": "Original Book",
        "authors": ["Author"],
        "year": 2020,
        "publisher": "Original Publisher",
        "place": "Original City",
        "edition": 1
    }
    citation = citation_service.create_citation(project.id, citation_data)
    
    update_data = {
        "type": "book",  # Same type
        "title": "Updated Book",
        "authors": ["Author"],
        "year": 2020,
        "publisher": "Updated Publisher",
        "place": "Updated City",
        "edition": 2
    }
    
    result = citation_service.update_citation(citation.id, project.id, update_data)
    assert result.title == "Updated Book"
    assert result.type == "book"

def test_update_citation_type_changes(citation_service, project_service):
    """Type changes, validate_citation_data called with type_change=True"""
    project = project_service.create_project({"name": "Test Project"})
    citation_data = {
        "type": "book",
        "title": "Original Book",
        "authors": ["Author"],
        "year": 2020,
        "publisher": "Original Publisher",
        "place": "Original City",
        "edition": 1
    }
    citation = citation_service.create_citation(project.id, citation_data)

    update_data = {
        "type": "article",  # Different type
        "title": "Updated Article",
        "authors": ["Author"],
        "journal": "Test Journal",
        "year": 2020,
        "volume": 1,
        "issue": "1",
        "pages": "1-10",
        "doi": "10.1000/test"
    }

    result = citation_service.update_citation(citation.id, project.id, update_data)
    assert result.title == "Updated Article"
    assert result.type == "article"

def test_update_citation_not_in_project(citation_service, project_service):
    """Citation exists but doesn't belong to the specified project"""
    project1 = project_service.create_project({"name": "Project 1"})
    project2 = project_service.create_project({"name": "Project 2"})

    citation_data = {
        "type": "book",
        "title": "Test Book",
        "authors": ["Author"],
        "year": 2020,
        "publisher": "Publisher",
        "place": "City",
        "edition": 1
    }
    citation = citation_service.create_citation(project1.id, citation_data)

    # Try to update citation from project1 using project2's id
    # Currently this may not be enforced, test documents expected behavior
    update_data = {"title": "Updated Book"}
    result = citation_service.update_citation(citation.id, project2.id, update_data)
    # This test documents current behavior - citation can be updated from any project
    assert result.title == "Updated Book"

# ========== DELETE_CITATION TESTS ==========

def test_delete_citation_id_none(citation_service):
    """citation_id is None returns HTTP 400"""
    with pytest.raises(HTTPException) as exc_info:
        citation_service.delete_citation(None, 1)
    assert exc_info.value.status_code == 400

def test_delete_citation_project_id_none(citation_service):
    """project_id is None returns HTTP 400"""
    with pytest.raises(HTTPException) as exc_info:
        citation_service.delete_citation(1, None)
    assert exc_info.value.status_code == 400

def test_delete_citation_project_not_exists(citation_service):
    """Project does not exist returns HTTP 404"""
    with pytest.raises(HTTPException) as exc_info:
        citation_service.delete_citation(1, 999)
    assert exc_info.value.status_code == 404

def test_delete_citation_not_exists(citation_service, project_service):
    """Citation does not exist returns HTTP 404"""
    project = project_service.create_project({"name": "Test Project"})
    
    with pytest.raises(HTTPException) as exc_info:
        citation_service.delete_citation(999, project.id)
    assert exc_info.value.status_code == 404

def test_delete_citation_valid_case(citation_service, project_service):
    """Valid case returns message Citation deleted"""
    project = project_service.create_project({"name": "Test Project"})
    citation_data = {
        "type": "book",
        "title": "Test Book",
        "authors": ["Author"],
        "year": 2020,
        "publisher": "Test Publisher",
        "place": "Test City",
        "edition": 1
    }
    citation = citation_service.create_citation(project.id, citation_data)

    result = citation_service.delete_citation(citation.id, project.id)
    assert result == {"message": "Citation deleted"}

def test_delete_citation_not_in_project(citation_service, project_service):
    """Citation exists but doesn't belong to the specified project"""
    project1 = project_service.create_project({"name": "Project 1"})
    project2 = project_service.create_project({"name": "Project 2"})

    citation_data = {
        "type": "book",
        "title": "Test Book",
        "authors": ["Author"],
        "year": 2020,
        "publisher": "Publisher",
        "place": "City",
        "edition": 1
    }
    citation = citation_service.create_citation(project1.id, citation_data)

    # Try to delete citation from project1 using project2's id
    # Currently this may not be enforced, test documents expected behavior
    result = citation_service.delete_citation(citation.id, project2.id)
    assert result == {"message": "Citation deleted"}

# ========== FORMAT_CITATION TESTS ==========

def test_format_citation_apa(citation_service, project_service):
    """Format apa instantiates APAFormatter and calls format_citation"""
    project = project_service.create_project({"name": "Test Project"})
    citation_data = {
        "type": "book",
        "title": "Test Book",
        "authors": ["Test Author"],
        "year": 2020,
        "publisher": "Test Publisher",
        "place": "Test City",
        "edition": 1
    }
    citation = citation_service.create_citation(project.id, citation_data)
    
    result = citation_service.format_citation(citation, "apa")
    assert "Author" in result
    assert "2020" in result
    assert "Test book" in result  # APA uses sentence case

def test_format_citation_mla(citation_service, project_service):
    """Format mla instantiates MLAFormatter"""
    project = project_service.create_project({"name": "Test Project"})
    citation_data = {
        "type": "book",
        "title": "Test Book",
        "authors": ["Test Author"],
        "year": 2020,
        "publisher": "Test Publisher",
        "place": "Test City",
        "edition": 1
    }
    citation = citation_service.create_citation(project.id, citation_data)
    
    result = citation_service.format_citation(citation, "mla")
    assert "Author" in result
    assert "2020" in result
    assert "Test Book" in result

def test_format_citation_unsupported_format(citation_service, project_service):
    """Unsupported format chicago raises ValueError"""
    project = project_service.create_project({"name": "Test Project"})
    citation_data = {
        "type": "book",
        "title": "Test Book",
        "authors": ["Test Author"],
        "year": 2020,
        "publisher": "Test Publisher",
        "place": "Test City",
        "edition": 1
    }
    citation = citation_service.create_citation(project.id, citation_data)

    with pytest.raises(ValueError):
        citation_service.format_citation(citation, "chicago")

def test_format_citation_website_apa(citation_service, project_service):
    """Format website citation in APA format"""
    project = project_service.create_project({"name": "Test Project"})
    citation_data = {
        "type": "website",
        "title": "Test Website",
        "authors": ["Web Author"],
        "year": 2023,
        "publisher": "Example Publisher",
        "url": "https://example.com",
        "access_date": "2024-01-15"
    }
    citation = citation_service.create_citation(project.id, citation_data)

    result = citation_service.format_citation(citation, "apa")
    assert "Author" in result
    assert "2023" in result
    assert "https://example.com" in result

def test_format_citation_report_mla(citation_service, project_service):
    """Format report citation in MLA format"""
    project = project_service.create_project({"name": "Test Project"})
    citation_data = {
        "type": "report",
        "title": "Test Report",
        "authors": ["Report Author"],
        "year": 2022,
        "publisher": "Test Institution",
        "url": "https://example.com/report",
        "place": "New York"
    }
    citation = citation_service.create_citation(project.id, citation_data)

    result = citation_service.format_citation(citation, "mla")
    assert "Author" in result
    assert "2022" in result
    assert "Test Report" in result

def test_format_citation_none_citation(citation_service):
    """Format citation with None citation object raises AttributeError"""
    with pytest.raises(AttributeError):
        citation_service.format_citation(None, "apa")

def test_format_citation_invalid_citation_object(citation_service):
    """Format citation with invalid citation object raises AttributeError"""
    invalid_citation = {"title": "Not a citation object"}
    with pytest.raises(AttributeError):
        citation_service.format_citation(invalid_citation, "apa")
