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

def test_delete_project_with_no_citations(db_session):
    repo = ProjectRepository(db_session)
    
    project = repo.create("Empty Project")
    project_id = project.id
    
    result = repo.delete(project_id)
    
    assert result is True
    assert repo.get_by_id(project_id) is None

def test_delete_project_not_found(db_session):
    repo = ProjectRepository(db_session)
    
    result = repo.delete(999)
    
    assert result is False

def test_delete_project_with_unique_citations(db_session):
    project_repo = ProjectRepository(db_session)
    citation_repo = CitationRepository(db_session)
    
    project = project_repo.create("Project with Unique Citations")
    
    # Crear citas únicas para este proyecto
    citation1 = citation_repo.create(
        project_id=project.id,
        type="book",
        title="Unique Book 1",
        authors=["Author A"],
        year=2020
    )
    citation2 = citation_repo.create(
        project_id=project.id,
        type="article", 
        title="Unique Article 1",
        authors=["Author B"],
        year=2021
    )
    
    citation1_id = citation1.id
    citation2_id = citation2.id
    
    result = project_repo.delete(project.id)
    
    assert result is True
    assert project_repo.get_by_id(project.id) is None
    
    assert citation_repo.get_by_id(citation1_id) is None
    assert citation_repo.get_by_id(citation2_id) is None
    
    remaining_assocs = (
        db_session.query(ProjectCitation)
        .filter(ProjectCitation.project_id == project.id)
        .count()
    )
    assert remaining_assocs == 0

def test_delete_project_with_shared_citations(db_session):
    project_repo = ProjectRepository(db_session)
    citation_repo = CitationRepository(db_session)
    
    project1 = project_repo.create("Project 1 - Shared")
    project2 = project_repo.create("Project 2 - Shared")
    
    shared_citation = citation_repo.create(
        project_id=project1.id,
        type="book",
        title="Shared Book",
        authors=["Shared Author"],
        year=2020
    )

    citation_repo.create(
        project_id=project2.id,
        type="book",
        title="Shared Book", 
        authors=["Shared Author"],
        year=2020
    )
    
    citation_id = shared_citation.id
    
    result = project_repo.delete(project1.id)
    
    assert result is True
    assert project_repo.get_by_id(project1.id) is None
    
    assert citation_repo.get_by_id(citation_id) is not None
    
    project2_citations = citation_repo.get_all_by_project(project2.id)
    assert len(project2_citations) == 1
    assert project2_citations[0].id == citation_id

def test_delete_project_mixed_citations(db_session):
    project_repo = ProjectRepository(db_session)
    citation_repo = CitationRepository(db_session)
    
    project_to_delete = project_repo.create("Project to Delete")
    other_project = project_repo.create("Other Project")

    unique_citation = citation_repo.create(
        project_id=project_to_delete.id,
        type="book",
        title="Unique Book",
        authors=["Unique Author"],
        year=2020
    )
    
    shared_citation = citation_repo.create(
        project_id=project_to_delete.id,
        type="article",
        title="Shared Article", 
        authors=["Shared Author"],
        year=2021
    )
    
    citation_repo.create(
        project_id=other_project.id,
        type="article",
        title="Shared Article",
        authors=["Shared Author"],
        year=2021
    )
    
    unique_id = unique_citation.id
    shared_id = shared_citation.id

    result = project_repo.delete(project_to_delete.id)
    
    assert result is True
    assert project_repo.get_by_id(project_to_delete.id) is None
    assert citation_repo.get_by_id(unique_id) is None
    assert citation_repo.get_by_id(shared_id) is not None
    other_citations = citation_repo.get_all_by_project(other_project.id)
    assert len(other_citations) == 1
    assert other_citations[0].id == shared_id

def test_delete_project_cascade_integrity(db_session):
    project_repo = ProjectRepository(db_session)
    citation_repo = CitationRepository(db_session)
    
    project = project_repo.create("Cascade Test Project")
    
    citation = citation_repo.create(
        project_id=project.id,
        type="article",
        title="Test Citation",
        authors=["Test Author"],
        year=2020
    )
    
    assoc_before = (
        db_session.query(ProjectCitation)
        .filter(ProjectCitation.project_id == project.id)
        .count()
    )
    assert assoc_before == 1

    result = project_repo.delete(project.id)
    
    assert result is True
    
    assoc_after = (
        db_session.query(ProjectCitation)
        .filter(ProjectCitation.project_id == project.id)
        .count()
    )
    assert assoc_after == 0

def test_delete_project_multiple_citations_performance(db_session):
    project_repo = ProjectRepository(db_session)
    citation_repo = CitationRepository(db_session)
    
    project = project_repo.create("Performance Test Project")
    
    citations = []
    for i in range(10):
        citation = citation_repo.create(
            project_id=project.id,
            type="article",
            title=f"Test Article {i}",
            authors=[f"Author {i}"],
            year=2020 + i
        )
        citations.append(citation.id)
    
    result = project_repo.delete(project.id)
    
    assert result is True
    assert project_repo.get_by_id(project.id) is None

    for citation_id in citations:
        assert citation_repo.get_by_id(citation_id) is None
    
    remaining_assocs = (
        db_session.query(ProjectCitation)
        .filter(ProjectCitation.project_id == project.id)
        .count()
    )
    assert remaining_assocs == 0