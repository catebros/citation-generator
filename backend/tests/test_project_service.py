import pytest
from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.base import Base
from models.project import Project
from services.project_service import ProjectService
from repositories.project_repo import ProjectRepository
from repositories.citation_repo import CitationRepository
from services.validators.project_validator import (
    validate_project_data, 
    validate_unique_name,
    _validate_name
)

@pytest.fixture(scope="function")
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    yield session
    session.close()

@pytest.fixture
def project_service(db_session):
    return ProjectService(db_session)

def test_create_project_success(project_service):
    data = {"name": "Valid Project"}
    project = project_service.create_project(data)
    
    assert project.name == "Valid Project"
    assert project.id is not None

def test_create_project_empty_name_raises_400(project_service):
    with pytest.raises(HTTPException) as exc_info:
        project_service.create_project({"name": ""})
    
    assert exc_info.value.status_code == 400
    assert "cannot be empty" in exc_info.value.detail

def test_create_project_whitespace_name_raises_400(project_service):
    with pytest.raises(HTTPException) as exc_info:
        project_service.create_project({"name": "   "})
    
    assert exc_info.value.status_code == 400
    assert "cannot be empty" in exc_info.value.detail

def test_create_project_missing_name_raises_400(project_service):
    with pytest.raises(HTTPException) as exc_info:
        project_service.create_project({})
    
    assert exc_info.value.status_code == 400
    assert "cannot be empty" in exc_info.value.detail

def test_create_project_duplicate_name_raises_400(project_service):
    project_service.create_project({"name": "Duplicate Name"})
    
    with pytest.raises(HTTPException) as exc_info:
        project_service.create_project({"name": "Duplicate Name"})
    
    assert exc_info.value.status_code == 400
    assert "already exists" in exc_info.value.detail

def test_get_project_success(project_service):
    created = project_service.create_project({"name": "Test Project"})
    
    retrieved = project_service.get_project(created.id)
    
    assert retrieved.id == created.id
    assert retrieved.name == "Test Project"

def test_get_project_not_found_raises_404(project_service):
    with pytest.raises(HTTPException) as exc_info:
        project_service.get_project(999)
    
    assert exc_info.value.status_code == 404
    assert "not found" in exc_info.value.detail

def test_update_project_success(project_service):
    created = project_service.create_project({"name": "Original Name"})
    
    updated = project_service.update_project(created.id, {"name": "Updated Name"})
    
    assert updated.id == created.id
    assert updated.name == "Updated Name"

def test_update_project_not_found_raises_404(project_service):
    with pytest.raises(HTTPException) as exc_info:
        project_service.update_project(999, {"name": "New Name"})
    
    assert exc_info.value.status_code == 404
    assert "not found" in exc_info.value.detail

def test_delete_project_success(project_service):
    created = project_service.create_project({"name": "To Delete"})
    
    result = project_service.delete_project(created.id)
    
    assert result["message"] == "Project deleted"

def test_delete_project_not_found_raises_404(project_service):
    with pytest.raises(HTTPException) as exc_info:
        project_service.delete_project(999)
    
    assert exc_info.value.status_code == 404
    assert "not found" in exc_info.value.detail

def test_get_all_citations_by_project_success(project_service, db_session):
    created = project_service.create_project({"name": "Citation Project"})
    
    citations = project_service.get_all_citations_by_project(created.id)
    
    assert isinstance(citations, list)
    assert len(citations) == 0 

def test_get_all_citations_by_project_not_found_raises_404(project_service):
    with pytest.raises(HTTPException) as exc_info:
        project_service.get_all_citations_by_project(999)
    
    assert exc_info.value.status_code == 404
    assert "not found" in exc_info.value.detail

def test_get_all_projects_returns_list(project_service):
    projects = project_service.get_all_projects()
    assert isinstance(projects, list)
    assert len(projects) == 0
    
    project_service.create_project({"name": "Project 1"})
    project_service.create_project({"name": "Project 2"})
    
    projects = project_service.get_all_projects()
    assert len(projects) == 2

def test_service_uses_repo_correctly(project_service, db_session):
    assert isinstance(project_service.project_repo, ProjectRepository)
    assert isinstance(project_service.citation_repo, CitationRepository)
    
    assert project_service.project_repo.db is db_session
    assert project_service.citation_repo.db is db_session
    
def test_validate_project_data_with_valid_name():
    """Test validation passes for valid data with name."""
    data = {"name": "Valid Project Name"}
    assert validate_project_data(data, mode="create") is True

def test_validate_project_data_update_mode():
    """Test validation passes for update mode."""
    data = {"name": "Updated Project Name"}
    assert validate_project_data(data, mode="update") is True

def test_name_validation_valid_name_passes():
    """Test that valid name passes validation."""
    _validate_name("Valid Project Name", "name")  # Should not raise

def test_name_validation_non_string_raises_400():
    """Test that non-string name raises HTTPException."""
    with pytest.raises(HTTPException) as exc_info:
        _validate_name(123, "name")
    
    assert exc_info.value.status_code == 400
    assert "must be a non-empty string" in exc_info.value.detail

def test_name_validation_empty_name_raises_400():
    """Test that empty name raises HTTPException."""
    empty_names = ["", "   ", "\t\n"]
    
    for name in empty_names:
        with pytest.raises(HTTPException) as exc_info:
            _validate_name(name, "name")
        
        assert exc_info.value.status_code == 400
        assert "must be a non-empty string" in exc_info.value.detail

def test_unique_name_validation_passes():
    """Test that unique name passes validation."""
    class MockRepo:
        def get_by_name(self, name):
            return None
    
    repo = MockRepo()
    assert validate_unique_name("Unique Name", repo) is True

def test_unique_name_validation_duplicate_raises_400():
    """Test that duplicate name raises HTTPException."""
    class MockProject:
        def __init__(self, id, name):
            self.id = id
            self.name = name
    
    class MockRepo:
        def get_by_name(self, name):
            return MockProject(1, name)
    
    repo = MockRepo()
    with pytest.raises(HTTPException) as exc_info:
        validate_unique_name("Duplicate Name", repo)
    
    assert exc_info.value.status_code == 400
    assert "already exists" in exc_info.value.detail

def test_unique_name_validation_with_exclude_id_passes():
    """Test that duplicate name passes when exclude_id matches."""
    class MockProject:
        def __init__(self, id, name):
            self.id = id
            self.name = name
    
    class MockRepo:
        def get_by_name(self, name):
            return MockProject(1, name)
    
    repo = MockRepo()
    assert validate_unique_name("Duplicate Name", repo, exclude_id=1) is True

def test_unique_name_validation_with_different_exclude_id_raises_400():
    """Test that duplicate name raises exception when exclude_id is different."""
    class MockProject:
        def __init__(self, id, name):
            self.id = id
            self.name = name
    
    class MockRepo:
        def get_by_name(self, name):
            return MockProject(1, name)
    
    repo = MockRepo()
    with pytest.raises(HTTPException) as exc_info:
        validate_unique_name("Duplicate Name", repo, exclude_id=2)
    
    assert exc_info.value.status_code == 400
    assert "already exists" in exc_info.value.detail