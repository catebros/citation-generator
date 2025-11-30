# backend/tests/test_project_service.py
import pytest
from fastapi import HTTPException
from models.base import Base
from services.citation_service import CitationService
from services.project_service import ProjectService
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


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


def test_create_project_data_none(project_service):
    """data is None returns HTTP 400"""
    with pytest.raises(HTTPException) as exc_info:
        project_service.create_project(None)
    assert exc_info.value.status_code == 400


def test_create_project_validation_error(project_service):
    """validate_project_data raises exception and it propagates"""
    with pytest.raises(HTTPException) as exc_info:
        project_service.create_project(
            {"name": ""}
        )  # Empty name should fail validation
    assert exc_info.value.status_code == 400


def test_create_project_name_exists(project_service):
    """Name already exists returns HTTP 409"""
    # Create first project
    project_service.create_project({"name": "Existing Project"})

    # Try to create project with same name
    with pytest.raises(HTTPException) as exc_info:
        project_service.create_project({"name": "Existing Project"})
    assert exc_info.value.status_code == 409


def test_create_project_valid_case(project_service):
    """Valid case calls validate_project_data and _project_repo.create"""
    project_data = {"name": "Valid Project"}
    result = project_service.create_project(project_data)

    assert result.name == "Valid Project"
    assert result.id is not None


def test_get_project_id_none(project_service):
    """project_id is None returns HTTP 400"""
    with pytest.raises(HTTPException) as exc_info:
        project_service.get_project(None)
    assert exc_info.value.status_code == 400


def test_get_project_not_exists(project_service):
    """Project does not exist returns HTTP 404"""
    with pytest.raises(HTTPException) as exc_info:
        project_service.get_project(999)
    assert exc_info.value.status_code == 404


def test_get_project_found(project_service):
    """Project found returns object"""
    # Create project first
    created_project = project_service.create_project({"name": "Test Project"})

    # Get project
    result = project_service.get_project(created_project.id)
    assert result.id == created_project.id
    assert result.name == "Test Project"


def test_get_all_projects_empty(project_service):
    """Returns empty list when no projects exist"""
    result = project_service.get_all_projects()
    assert len(result) == 0
    assert result == []


def test_get_all_projects(project_service):
    """Returns list of projects"""
    # Create some projects
    project_service.create_project({"name": "Project 1"})
    project_service.create_project({"name": "Project 2"})

    result = project_service.get_all_projects()
    assert len(result) == 2

    project_names = [p.name for p in result]
    assert "Project 1" in project_names
    assert "Project 2" in project_names


def test_update_project_id_none(project_service):
    """project_id is None returns HTTP 400"""
    with pytest.raises(HTTPException) as exc_info:
        project_service.update_project(None, {"name": "Updated"})
    assert exc_info.value.status_code == 400


def test_update_project_data_none(project_service):
    """data is None returns HTTP 400"""
    with pytest.raises(HTTPException) as exc_info:
        project_service.update_project(1, None)
    assert exc_info.value.status_code == 400


def test_update_project_not_exists(project_service):
    """Project does not exist returns HTTP 404"""
    with pytest.raises(HTTPException) as exc_info:
        project_service.update_project(999, {"name": "Updated"})
    assert exc_info.value.status_code == 404


def test_update_project_name_duplicate(project_service):
    """Duplicate name in another project returns HTTP 409"""
    # Create two projects
    project_service.create_project({"name": "Project 1"})
    project2 = project_service.create_project({"name": "Project 2"})

    # Try to update project2 to have same name as project1
    with pytest.raises(HTTPException) as exc_info:
        project_service.update_project(project2.id, {"name": "Project 1"})
    assert exc_info.value.status_code == 409


def test_update_project_valid_case(project_service):
    """Valid case calls validate_project_data and update returns updated project"""
    # Create project
    project = project_service.create_project({"name": "Original Name"})

    # Update project
    result = project_service.update_project(project.id, {"name": "Updated Name"})
    assert result.id == project.id
    assert result.name == "Updated Name"


def test_update_project_validation_error(project_service):
    """Validation error with empty name returns HTTP 400"""
    # Create project
    project = project_service.create_project({"name": "Original Name"})

    # Try to update with empty name
    with pytest.raises(HTTPException) as exc_info:
        project_service.update_project(project.id, {"name": ""})
    assert exc_info.value.status_code == 400


def test_update_project_same_name(project_service):
    """Updating project with its own name should succeed"""
    # Create project
    project = project_service.create_project({"name": "Project Name"})

    # Update with same name (should succeed)
    result = project_service.update_project(project.id, {"name": "Project Name"})
    assert result.id == project.id
    assert result.name == "Project Name"


def test_delete_project_id_none(project_service):
    """project_id is None returns HTTP 400"""
    with pytest.raises(HTTPException) as exc_info:
        project_service.delete_project(None)
    assert exc_info.value.status_code == 400


def test_delete_project_not_exists(project_service):
    """Project does not exist returns HTTP 404"""
    with pytest.raises(HTTPException) as exc_info:
        project_service.delete_project(999)
    assert exc_info.value.status_code == 404


def test_delete_project_valid_case(project_service):
    """Valid case returns message Project deleted"""
    # Create project
    project = project_service.create_project({"name": "Test Project"})

    # Delete project
    result = project_service.delete_project(project.id)
    assert result == {"message": "Project deleted successfully"}


def test_delete_project_with_citations(project_service, db_session):
    """Deleting project with citations should succeed"""
    citation_service = CitationService(db_session)

    # Create project
    project = project_service.create_project({"name": "Test Project"})

    # Create citation
    citation_data = {
        "type": "book",
        "title": "Test Book",
        "authors": ["Test Author"],
        "year": 2020,
        "publisher": "Test Publisher",
        "place": "Test City",
        "edition": 1,
    }
    citation_service.create_citation(project.id, citation_data)

    # Delete project
    result = project_service.delete_project(project.id)
    assert result == {"message": "Project deleted successfully"}

    # Verify project is deleted
    with pytest.raises(HTTPException) as exc_info:
        project_service.get_project(project.id)
    assert exc_info.value.status_code == 404


def test_get_all_citations_by_project_id_none(project_service):
    """project_id is None returns HTTP 400"""
    with pytest.raises(HTTPException) as exc_info:
        project_service.get_all_citations_by_project(None)
    assert exc_info.value.status_code == 400


def test_get_all_citations_by_project_not_exists(project_service):
    """Project does not exist returns HTTP 404"""
    with pytest.raises(HTTPException) as exc_info:
        project_service.get_all_citations_by_project(999)
    assert exc_info.value.status_code == 404


def test_get_all_citations_by_project_valid_case(project_service, db_session):
    """Valid case returns list of citations"""
    citation_service = CitationService(db_session)

    # Create project
    project = project_service.create_project({"name": "Test Project"})

    # Create citations
    citation_data = {
        "type": "book",
        "title": "Test Book",
        "authors": ["Test Author"],
        "year": 2020,
        "publisher": "Test Publisher",
        "place": "Test City",
        "edition": 1,
    }
    citation_service.create_citation(project.id, citation_data)

    # Get citations
    result = project_service.get_all_citations_by_project(project.id)
    assert len(result) == 1
    assert result[0].title == "Test Book"


def test_get_all_citations_by_project_multiple(project_service, db_session):
    """Returns multiple citations for project"""
    citation_service = CitationService(db_session)

    # Create project
    project = project_service.create_project({"name": "Test Project"})

    # Create multiple citations
    citation_data1 = {
        "type": "book",
        "title": "Book One",
        "authors": ["Author One"],
        "year": 2020,
        "publisher": "Publisher A",
        "place": "City A",
        "edition": 1,
    }
    citation_data2 = {
        "type": "article",
        "title": "Article Two",
        "authors": ["Author Two"],
        "year": 2021,
        "journal": "Journal B",
        "volume": 1,
        "issue": "1",
        "pages": "1-10",
        "doi": "10.1000/test",
    }
    citation_service.create_citation(project.id, citation_data1)
    citation_service.create_citation(project.id, citation_data2)

    # Get citations
    result = project_service.get_all_citations_by_project(project.id)
    assert len(result) == 2

    titles = [c.title for c in result]
    assert "Book One" in titles
    assert "Article Two" in titles


def test_get_all_citations_by_project_empty(project_service):
    """Project with no citations returns empty list"""
    # Create project without citations
    project = project_service.create_project({"name": "Empty Project"})

    # Get citations
    result = project_service.get_all_citations_by_project(project.id)
    assert len(result) == 0
    assert result == []


def test_generate_bibliography_project_id_none(project_service):
    """project_id is None returns HTTP 400"""
    with pytest.raises(HTTPException) as exc_info:
        project_service.generate_bibliography_by_project(None, "apa")
    assert exc_info.value.status_code == 400


def test_generate_bibliography_project_not_exists(project_service):
    """Project does not exist returns HTTP 404"""
    with pytest.raises(HTTPException) as exc_info:
        project_service.generate_bibliography_by_project(999, "apa")
    assert exc_info.value.status_code == 404


def test_generate_bibliography_no_citations(project_service):
    """Project without citations returns dict with citation_count=0"""
    # Create project without citations
    project = project_service.create_project({"name": "Empty Project"})

    result = project_service.generate_bibliography_by_project(project.id, "apa")
    assert result["citation_count"] == 0
    assert result["bibliography"] == []


def test_generate_bibliography_with_citations(project_service, db_session):
    """Project with valid citations calls CitationService.format_citation and returns list"""
    citation_service = CitationService(db_session)

    # Create project
    project = project_service.create_project({"name": "Test Project"})

    # Create citations
    citation_data = {
        "type": "book",
        "title": "Test Book",
        "authors": ["Test Author"],
        "year": 2020,
        "publisher": "Test Publisher",
        "place": "Test City",
        "edition": 1,
    }
    citation_service.create_citation(project.id, citation_data)

    result = project_service.generate_bibliography_by_project(project.id, "apa")
    assert result["citation_count"] == 1
    assert len(result["bibliography"]) == 1
    assert "Author" in result["bibliography"][0]


def test_generate_bibliography_unsupported_format_fallback(project_service, db_session):
    """Unsupported format in citation falls back to APA"""
    citation_service = CitationService(db_session)

    # Create project
    project = project_service.create_project({"name": "Test Project"})

    # Create citation
    citation_data = {
        "type": "book",
        "title": "Test Book",
        "authors": ["Test Author"],
        "year": 2020,
        "publisher": "Test Publisher",
        "place": "Test City",
        "edition": 1,
    }
    citation_service.create_citation(project.id, citation_data)

    # Try unsupported format - should fallback to APA
    result = project_service.generate_bibliography_by_project(project.id, "chicago")
    assert result["citation_count"] == 1
    assert len(result["bibliography"]) == 1
    # Should still generate citation using fallback
    assert "Author" in result["bibliography"][0]


def test_generate_bibliography_mla_format(project_service, db_session):
    """Generate bibliography with MLA format"""
    citation_service = CitationService(db_session)

    # Create project
    project = project_service.create_project({"name": "Test Project"})

    # Create citation
    citation_data = {
        "type": "book",
        "title": "Test Book",
        "authors": ["Test Author"],
        "year": 2020,
        "publisher": "Test Publisher",
        "place": "Test City",
        "edition": 1,
    }
    citation_service.create_citation(project.id, citation_data)

    # Generate bibliography in MLA format
    result = project_service.generate_bibliography_by_project(project.id, "mla")
    assert result["citation_count"] == 1
    assert result["format_type"] == "mla"
    assert len(result["bibliography"]) == 1
    assert "Author" in result["bibliography"][0]
    assert "Test Book" in result["bibliography"][0]
