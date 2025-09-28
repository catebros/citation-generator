import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.base import Base
from models.project import Project
from models.citation import Citation
from models.project_citation import ProjectCitation
from repositories.project_repo import ProjectRepository
from repositories.citation_repo import CitationRepository

@pytest.fixture(scope="function")
def db_session():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    TestingSessionLocal = sessionmaker(bind=engine)
    Base.metadata.create_all(engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

def test_create_project(db_session):
    repo = ProjectRepository(db_session)
    project = repo.create(name="AI Thesis")

    assert project.id is not None
    assert project.name == "AI Thesis"

def test_get_project_by_id(db_session):
    repo = ProjectRepository(db_session)
    created = repo.create(name="ML Project")
    fetched = repo.get_by_id(created.id)

    assert fetched is not None
    assert fetched.id == created.id
    assert fetched.name == "ML Project"

def test_get_project_by_id_not_found(db_session):
    repo = ProjectRepository(db_session)
    fetched = repo.get_by_id(999)
    assert fetched is None

def test_get_all_projects(db_session):
    repo = ProjectRepository(db_session)
    repo.create(name="Project 1")
    repo.create(name="Project 2")

    projects = repo.get_all()
    assert len(projects) == 2
    names = [p.name for p in projects]
    assert "Project 1" in names
    assert "Project 2" in names

def test_update_project_name(db_session):
    repo = ProjectRepository(db_session)
    project = repo.create(name="Old Project")

    updated = repo.update(project.id, name="Updated Project")
    assert updated is not None
    assert updated.name == "Updated Project"

def test_update_project_not_found(db_session):
    repo = ProjectRepository(db_session)
    result = repo.update(999, name="Doesn't exist")
    assert result is None
