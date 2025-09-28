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
        "project_id": project.id,
        "type": "article",
        "title": "Test Article",
        "authors": ["Author One"],
        "year": 2023
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
        "year": 2023
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
        "year": 2022
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
        "year": 2020
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
        "year": 2020
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
        "year": 2020
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
        "year": 2020
    }
    
    citation = citation_service.create_citation(project.id, citation_data)

    assert citation is not None
    assert isinstance(citation.id, int)