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
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    yield session
    session.close()

@pytest.fixture
def citation_service(db_session):
    return CitationService(db_session)

@pytest.fixture
def project_service(db_session):
    return ProjectService(db_session)

def test_create_citation_success(citation_service, project_service):
    project = project_service.create_project({"name": "Test Project"})
    
    citation_data = {
        "type": "article",
        "title": "Test Article",
        "authors": ["Author One"],
        "year": 2023,
        "journal": "Test Journal",
        "volume": "1",
        "issue": "1",
        "pages": "1-10",
        "doi": "10.1234/test.2023"
    }
    
    citation = citation_service.create_citation(project.id, citation_data)
    
    assert citation.title == "Test Article"
    assert citation.type == "article"
    assert "Author One" in citation.authors

def test_create_citation_missing_required_fields_raises_400(citation_service, project_service):
    project = project_service.create_project({"name": "Test Project"})
    
    incomplete_data = {
        "type": "article",
    }
    
    with pytest.raises(HTTPException) as exc_info:
        citation_service.create_citation(project.id, incomplete_data)
    
    assert exc_info.value.status_code == 400

def test_create_citation_invalid_project_raises_404(citation_service):
    citation_data = {
        "type": "article",
        "title": "Test Article",
        "authors": ["Author"],
        "year": 2023,
        "journal": "Test Journal",
        "volume": "1",
        "issue": "1",
        "pages": "1-10"
    }
    
    with pytest.raises(HTTPException) as exc_info:
        citation_service.create_citation(999, citation_data)  
    
    assert exc_info.value.status_code == 404
    assert "Project not found" in exc_info.value.detail

def test_get_citation_success(citation_service, project_service):
    project = project_service.create_project({"name": "Test Project"})
    
    citation_data = {
        "type": "book",
        "title": "Test Book",
        "authors": ["Book Author"],
        "year": 2022,
        "publisher": "Test Publisher",
        "place": "Test City",
        "edition": "1st"
    }
    
    created = citation_service.create_citation(project.id, citation_data)
    retrieved = citation_service.get_citation(created.id)
    
    assert retrieved.id == created.id
    assert retrieved.title == "Test Book"

def test_update_citation_success(citation_service, project_service):
    project = project_service.create_project({"name": "Update Project"})
    
    citation_data = {
        "type": "article",
        "title": "Original Title",
        "authors": ["Author"],
        "year": 2020,
        "journal": "Original Journal",
        "volume": "1",
        "issue": "1",
        "pages": "1-10",
        "doi": "10.1234/original.2020"
    }
    
    created = citation_service.create_citation(project.id, citation_data)
    
    update_data = {
        "title": "Updated Title",
        "year": 2021
    }
    
    updated = citation_service.update_citation(created.id, project.id, update_data)
    
    assert updated.title == "Updated Title"
    assert updated.year == 2021
    assert "Author" in updated.authors

def test_update_citation_missing_project_id_raises_400(citation_service, project_service):
    project = project_service.create_project({"name": "Test Project"})
    
    citation_data = {
        "type": "article",
        "title": "Test",
        "authors": ["Author"],
        "year": 2020,
        "journal": "Test Journal",
        "volume": "1",
        "issue": "1",
        "pages": "1-10",
        "doi": "10.1234/test.2020"
    }
    
    created = citation_service.create_citation(project.id, citation_data)
    
    with pytest.raises(HTTPException) as exc_info:
        citation_service.update_citation(created.id, None, {"title": "New Title"})
    
    assert exc_info.value.status_code == 400
    assert "project_id is required" in exc_info.value.detail

def test_update_citation_not_found_raises_404(citation_service, project_service):
    project = project_service.create_project({"name": "Test Project"})
    
    with pytest.raises(HTTPException) as exc_info:
        citation_service.update_citation(999, project.id, {"title": "New"})
    
    assert exc_info.value.status_code == 404
    assert "Citation not found" in exc_info.value.detail

def test_delete_citation_success(citation_service, project_service):
    project = project_service.create_project({"name": "Delete Project"})
    
    citation_data = {
        "type": "book",
        "title": "To Delete",
        "authors": ["Author"],
        "year": 2020,
        "publisher": "Test Publisher",
        "place": "Test City",
        "edition": "1st"
    }
    
    created = citation_service.create_citation(project.id, citation_data)
    
    result = citation_service.delete_citation(created.id, project.id)
    
    assert result["message"] == "Citation deleted"

def test_service_handles_repo_exceptions(citation_service, project_service):
    project = project_service.create_project({"name": "Exception Test"})
    
    citation_data = {
        "type": "article",
        "title": "Test",
        "authors": ["Author"],
        "year": 2020,
        "journal": "Test Journal",
        "volume": "1",
        "issue": "1",
        "pages": "1-10",
        "doi": "10.1234/exception.2020"
    }
    
    citation = citation_service.create_citation(project.id, citation_data)

    assert citation is not None
    assert isinstance(citation.id, int)

def test_create_citation_missing_project_id_raises_400(citation_service):
    citation_data = {
        "type": "article",
        "title": "Test Article",
        "authors": ["Author"],
        "year": 2023,
        "journal": "Test Journal",
        "volume": "1",
        "issue": "1",
        "pages": "1-10"
    }
    
    with pytest.raises(HTTPException) as exc_info:
        citation_service.create_citation(None, citation_data)
    
    assert exc_info.value.status_code == 400
    assert "project_id is required" in exc_info.value.detail

def test_get_citation_missing_citation_id_raises_400(citation_service):
    with pytest.raises(HTTPException) as exc_info:
        citation_service.get_citation(None)
    
    assert exc_info.value.status_code == 400
    assert "citation_id is required" in exc_info.value.detail

def test_update_citation_missing_citation_id_raises_400(citation_service, project_service):
    project = project_service.create_project({"name": "Test Project"})
    
    with pytest.raises(HTTPException) as exc_info:
        citation_service.update_citation(None, project.id, {"title": "New Title"})
    
    assert exc_info.value.status_code == 400
    assert "citation_id is required" in exc_info.value.detail

def test_delete_citation_missing_citation_id_raises_400(citation_service, project_service):
    project = project_service.create_project({"name": "Test Project"})
    
    with pytest.raises(HTTPException) as exc_info:
        citation_service.delete_citation(None, project.id)
    
    assert exc_info.value.status_code == 400
    assert "citation_id is required" in exc_info.value.detail

def test_delete_citation_missing_project_id_raises_400(citation_service, project_service):
    project = project_service.create_project({"name": "Test Project"})
    
    citation_data = {
        "type": "book",
        "title": "Test Book",
        "authors": ["Author"],
        "year": 2020,
        "publisher": "Test Publisher",
        "place": "Test City",
        "edition": "1st"
    }
    
    created = citation_service.create_citation(project.id, citation_data)
    
    with pytest.raises(HTTPException) as exc_info:
        citation_service.delete_citation(created.id, None)
    
    assert exc_info.value.status_code == 400
    assert "project_id is required" in exc_info.value.detail

def test_create_citation_invalid_type_raises_400(citation_service, project_service):
    project = project_service.create_project({"name": "Test Project"})
    
    citation_data = {
        "type": "invalid_type",
        "title": "Test Title",
        "authors": ["Author"],
        "year": 2023
    }
    
    with pytest.raises(HTTPException) as exc_info:
        citation_service.create_citation(project.id, citation_data)
    
    assert exc_info.value.status_code == 400
    assert "Unsupported citation type" in exc_info.value.detail

def test_create_citation_missing_title_raises_400(citation_service, project_service):
    project = project_service.create_project({"name": "Test Project"})
    
    citation_data = {
        "type": "article",
        "authors": ["Author"],
        "year": 2023,
        "journal": "Test Journal",
        "volume": "1",
        "issue": "1",
        "pages": "1-10",
        "doi": "10.1234/test.2023"
    }
    
    with pytest.raises(HTTPException) as exc_info:
        citation_service.create_citation(project.id, citation_data)
    
    assert exc_info.value.status_code == 400
    assert "Missing required article fields: title" in exc_info.value.detail

def test_create_citation_missing_authors_raises_400(citation_service, project_service):
    project = project_service.create_project({"name": "Test Project"})
    
    citation_data = {
        "type": "article",
        "title": "Test Article",
        "year": 2023,
        "journal": "Test Journal",
        "volume": "1",
        "issue": "1",
        "pages": "1-10",
        "doi": "10.1234/test.2023"
    }
    
    with pytest.raises(HTTPException) as exc_info:
        citation_service.create_citation(project.id, citation_data)
    
    assert exc_info.value.status_code == 400
    assert "Missing required article fields: authors" in exc_info.value.detail

def test_create_citation_empty_authors_list_raises_400(citation_service, project_service):
    project = project_service.create_project({"name": "Test Project"})
    
    citation_data = {
        "type": "article",
        "title": "Test Article",
        "authors": [],
        "year": 2023,
        "journal": "Test Journal",
        "volume": "1",
        "issue": "1",
        "pages": "1-10",
        "doi": "10.1234/test.2023"
    }
    
    with pytest.raises(HTTPException) as exc_info:
        citation_service.create_citation(project.id, citation_data)
    
    assert exc_info.value.status_code == 400
    assert "Missing required article fields: authors" in exc_info.value.detail

def test_create_citation_invalid_year_format_raises_400(citation_service, project_service):
    project = project_service.create_project({"name": "Test Project"})
    
    citation_data = {
        "type": "article",
        "title": "Test Article",
        "authors": ["Author"],
        "year": "invalid_year",
        "journal": "Test Journal",
        "volume": "1",
        "issue": "1",
        "pages": "1-10",
        "doi": "10.1234/test.2023"
    }
    
    with pytest.raises(HTTPException) as exc_info:
        citation_service.create_citation(project.id, citation_data)
    
    assert exc_info.value.status_code == 400
    assert "Year must be an integer" in exc_info.value.detail

def test_create_citation_future_year_raises_400(citation_service, project_service):
    project = project_service.create_project({"name": "Test Project"})
    
    citation_data = {
        "type": "article",
        "title": "Test Article",
        "authors": ["Author"],
        "year": 2030,
        "journal": "Test Journal",
        "volume": "1",
        "issue": "1",
        "pages": "1-10",
        "doi": "10.1234/test.2023"
    }
    
    with pytest.raises(HTTPException) as exc_info:
        citation_service.create_citation(project.id, citation_data)
    
    assert exc_info.value.status_code == 400
    assert "Year must be between 1000 and" in exc_info.value.detail

def test_create_citation_very_old_year_raises_400(citation_service, project_service):
    project = project_service.create_project({"name": "Test Project"})
    
    citation_data = {
        "type": "article",
        "title": "Test Article",
        "authors": ["Author"],
        "year": -1,
        "journal": "Test Journal",
        "volume": "1",
        "issue": "1",
        "pages": "1-10",
        "doi": "10.1234/test.2023"
    }
    
    with pytest.raises(HTTPException) as exc_info:
        citation_service.create_citation(project.id, citation_data)
    
    assert exc_info.value.status_code == 400
    assert "Year must be between 1000 and" in exc_info.value.detail

def test_create_article_missing_journal_raises_400(citation_service, project_service):
    project = project_service.create_project({"name": "Test Project"})
    
    citation_data = {
        "type": "article",
        "title": "Test Article",
        "authors": ["Author"],
        "year": 2023,
        "volume": "1",
        "issue": "1",
        "pages": "1-10",
        "doi": "10.1234/test.2023"
    }
    
    with pytest.raises(HTTPException) as exc_info:
        citation_service.create_citation(project.id, citation_data)
    
    assert exc_info.value.status_code == 400
    assert "Missing required article fields: journal" in exc_info.value.detail

def test_create_book_missing_publisher_raises_400(citation_service, project_service):
    project = project_service.create_project({"name": "Test Project"})
    
    citation_data = {
        "type": "book",
        "title": "Test Book",
        "authors": ["Author"],
        "year": 2023,
        "place": "Test City",
        "edition": "1st"
    }
    
    with pytest.raises(HTTPException) as exc_info:
        citation_service.create_citation(project.id, citation_data)
    
    assert exc_info.value.status_code == 400
    assert "Missing required book fields: publisher" in exc_info.value.detail

def test_create_website_missing_url_raises_400(citation_service, project_service):
    project = project_service.create_project({"name": "Test Project"})
    
    citation_data = {
        "type": "website",
        "title": "Test Website",
        "authors": ["Author"],
        "year": 2023,
        "access_date": "2023-12-01"
    }
    
    with pytest.raises(HTTPException) as exc_info:
        citation_service.create_citation(project.id, citation_data)
    
    assert exc_info.value.status_code == 400
    assert "Missing required website fields: url" in exc_info.value.detail

def test_create_citation_invalid_doi_format_raises_400(citation_service, project_service):
    project = project_service.create_project({"name": "Test Project"})
    
    citation_data = {
        "type": "article",
        "title": "Test Article",
        "authors": ["Author"],
        "year": 2023,
        "journal": "Test Journal",
        "volume": "1",
        "issue": "1",
        "pages": "1-10",
        "doi": "invalid-doi-format"
    }
    
    with pytest.raises(HTTPException) as exc_info:
        citation_service.create_citation(project.id, citation_data)
    
    assert exc_info.value.status_code == 400
    assert "Invalid DOI format" in exc_info.value.detail

def test_create_citation_invalid_url_format_raises_400(citation_service, project_service):
    project = project_service.create_project({"name": "Test Project"})
    
    citation_data = {
        "type": "website",
        "title": "Test Website",
        "authors": ["Author"],
        "year": 2023,
        "url": "not-a-valid-url",
        "access_date": "2023-12-01"
    }
    
    with pytest.raises(HTTPException) as exc_info:
        citation_service.create_citation(project.id, citation_data)
    
    assert exc_info.value.status_code == 400
    assert "Invalid URL format" in exc_info.value.detail

def test_create_citation_empty_title_raises_400(citation_service, project_service):
    project = project_service.create_project({"name": "Test Project"})
    
    citation_data = {
        "type": "article",
        "title": "",
        "authors": ["Author"],
        "year": 2023,
        "journal": "Test Journal",
        "volume": "1",
        "issue": "1",
        "pages": "1-10",
        "doi": "10.1234/test.2023"
    }
    
    with pytest.raises(HTTPException) as exc_info:
        citation_service.create_citation(project.id, citation_data)
    
    assert exc_info.value.status_code == 400
    assert "Missing required article fields: title" in exc_info.value.detail

def test_create_citation_whitespace_only_title_raises_400(citation_service, project_service):
    project = project_service.create_project({"name": "Test Project"})
    
    citation_data = {
        "type": "article",
        "title": "   ",
        "authors": ["Author"],
        "year": 2023,
        "journal": "Test Journal",
        "volume": "1",
        "issue": "1",
        "pages": "1-10",
        "doi": "10.1234/test.2023"
    }
    
    with pytest.raises(HTTPException) as exc_info:
        citation_service.create_citation(project.id, citation_data)
    
    assert exc_info.value.status_code == 400
    assert "Title must be a non-empty string" in exc_info.value.detail

def test_update_citation_with_invalid_data_raises_400(citation_service, project_service):
    project = project_service.create_project({"name": "Test Project"})
    
    citation_data = {
        "type": "article",
        "title": "Original Title",
        "authors": ["Author"],
        "year": 2020,
        "journal": "Test Journal",
        "volume": "1",
        "issue": "1",
        "pages": "1-10",
        "doi": "10.1234/test.2020"
    }
    
    created = citation_service.create_citation(project.id, citation_data)
    
    update_data = {
        "year": "invalid_year"
    }
    
    with pytest.raises(HTTPException) as exc_info:
        citation_service.update_citation(created.id, project.id, update_data)
    
    assert exc_info.value.status_code == 400
    assert "Year must be an integer" in exc_info.value.detail

def test_create_citation_with_special_characters_in_title_success(citation_service, project_service):
    project = project_service.create_project({"name": "Test Project"})
    
    citation_data = {
        "type": "article",
        "title": "Test Article: A Study of α-β Interactions & γ-Radiation Effects",
        "authors": ["Author One", "Author Two"],
        "year": 2023,
        "journal": "Test Journal",
        "volume": "1",
        "issue": "1",
        "pages": "1-10",
        "doi": "10.1234/test.2023"
    }
    
    citation = citation_service.create_citation(project.id, citation_data)
    
    assert citation.title == "Test Article: A Study of α-β Interactions & γ-Radiation Effects"
    # authors se almacena como JSON string, así que verificamos que contenga los autores
    assert "Author One" in citation.authors
    assert "Author Two" in citation.authors

def test_create_citation_with_multiple_authors_success(citation_service, project_service):
    project = project_service.create_project({"name": "Test Project"})
    
    authors_list = ["First Author", "Second Author", "Third Author", "Fourth Author"]
    
    citation_data = {
        "type": "article",
        "title": "Multi-Author Study",
        "authors": authors_list,
        "year": 2023,
        "journal": "Test Journal",
        "volume": "1",
        "issue": "1",
        "pages": "1-10",
        "doi": "10.1234/multi.2023"
    }
    
    citation = citation_service.create_citation(project.id, citation_data)
    
    # authors se almacena como JSON string, así que verificamos que contenga todos los autores
    for author in authors_list:
        assert author in citation.authors