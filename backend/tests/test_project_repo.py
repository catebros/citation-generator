import pytest
import time
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

# TEST FOR CREATE
# Creates a new project and verifies it has an ID and correct name
def test_create_project(db_session):
    repo = ProjectRepository(db_session)
    project = repo.create(name="AI Thesis")

    assert project.id is not None
    assert project.name == "AI Thesis"

# TEST FOR GET BY ID
# Retrieves a project by its ID and verifies all attributes match
def test_get_project_by_id(db_session):
    repo = ProjectRepository(db_session)
    created = repo.create(name="ML Project")
    fetched = repo.get_by_id(created.id)

    assert fetched is not None
    assert fetched.id == created.id
    assert fetched.name == "ML Project"

# Returns None when project ID doesn't exist
def test_get_project_by_id_not_found(db_session):
    repo = ProjectRepository(db_session)
    fetched = repo.get_by_id(999)
    assert fetched is None

# TEST FOR GET ALL
# Returns empty list when no projects exist and ensures proper ordering by created_at desc
def test_get_all_projects(db_session):
    repo = ProjectRepository(db_session)
    
    # Create projects with small delay to ensure different timestamps
    project1 = repo.create(name="Project 1")
    time.sleep(0.001)
    project2 = repo.create(name="Project 2")

    projects = repo.get_all()
    assert len(projects) == 2
    
    # Verify projects are ordered by created_at desc (newest first)
    assert projects[0].name == "Project 2"  # Most recent
    assert projects[1].name == "Project 1"  # Oldest
    
    names = [p.name for p in projects]
    assert "Project 1" in names
    assert "Project 2" in names

# Returns empty list when no projects exist
def test_get_all_projects_empty(db_session):
    repo = ProjectRepository(db_session)
    projects = repo.get_all()
    assert projects == []

# TEST UPDATE 
# Updates project name and ignores None values to preserve existing data
def test_update_project_name(db_session):
    repo = ProjectRepository(db_session)
    project = repo.create(name="Old Project")

    updated = repo.update(project.id, name="Updated Project")
    assert updated is not None
    assert updated.name == "Updated Project"

# Returns None when trying to update non-existent project
def test_update_project_not_found(db_session):
    repo = ProjectRepository(db_session)
    result = repo.update(999, name="Doesn't exist")
    assert result is None

# TEST DELETE
# Deletes project with no citations successfully
def test_delete_project_with_no_citations(db_session):
    repo = ProjectRepository(db_session)
    
    project = repo.create("Empty Project")
    project_id = project.id
    
    result = repo.delete(project_id)
    
    assert result is True
    assert repo.get_by_id(project_id) is None

# Returns False when trying to delete non-existent project
def test_delete_project_not_found(db_session):
    repo = ProjectRepository(db_session)
    
    result = repo.delete(999)
    
    assert result is False

# Deletes project and its unique citations (orphan cleanup)
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

# Deletes project but preserves shared citations used by other projects
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
    
    project2_citations = project_repo.get_all_by_project(project2.id)
    assert len(project2_citations) == 1
    assert project2_citations[0].id == citation_id

# Deletes project with mixed unique and shared citations
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
    other_citations = project_repo.get_all_by_project(other_project.id)
    assert len(other_citations) == 1
    assert other_citations[0].id == shared_id

# Verifies CASCADE integrity for ProjectCitation associations
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

# Tests deletion performance with multiple citations
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

# TEST GET BY NAME
# Returns project when it exists with the given name
def test_get_by_name_existing(db_session):
    repo = ProjectRepository(db_session)
    created = repo.create(name="Machine Learning Project")
    
    fetched = repo.get_by_name("Machine Learning Project")
    
    assert fetched is not None
    assert fetched.id == created.id
    assert fetched.name == "Machine Learning Project"

# Returns None when project with given name doesn't exist
def test_get_by_name_not_found(db_session):
    repo = ProjectRepository(db_session)
    
    fetched = repo.get_by_name("Non-existent Project")
    
    assert fetched is None

# TEST GET ALL BY PROJECT
# Returns citations ordered by created_at desc for a specific project
def test_get_all_by_project(db_session):
    project_repo = ProjectRepository(db_session)
    citation_repo = CitationRepository(db_session)

    project = project_repo.create("Thesis on AI")

    # Create citations with delay to ensure different timestamps
    citation1 = citation_repo.create(
        project_id=project.id,
        type="book",
        title="AI Foundations",
        authors=["Alan Turing"],
        year=1950
    )
    time.sleep(0.001)
    citation2 = citation_repo.create(
        project_id=project.id,
        type="article",
        title="Neural Nets",
        authors=["Geoff Hinton"],
        year=1986
    )

    results = project_repo.get_all_by_project(project.id)

    assert len(results) == 2
    
    # Verify ordering by created_at desc (newest first)
    assert results[0].title == "Neural Nets"  # Most recent
    assert results[1].title == "AI Foundations"  # Oldest
    
    titles = [c.title for c in results]
    assert "AI Foundations" in titles
    assert "Neural Nets" in titles

# Returns empty list when project has no citations
def test_get_all_by_project_empty(db_session):
    project_repo = ProjectRepository(db_session)

    project = project_repo.create("Empty Project")
    results = project_repo.get_all_by_project(project.id)

    assert results == []

# Returns empty list when project doesn't exist
def test_get_all_by_project_nonexistent_project(db_session):
    project_repo = ProjectRepository(db_session)

    results = project_repo.get_all_by_project(12345)
    assert results == []


# =========================================================
# OUT OF LAYER SCOPE TESTS (EXTRA)
# These tests cover situations that, according to the app’s logic,
# should never reach the repository layer because they are already
# validated at the service/validator layer. However, we include them
# here to ensure that the repository behaves safely and consistently
# when receiving unexpected or invalid data.
# =========================================================

def test_update_project_with_invalid_field_is_ignored(db_session):
    repo = ProjectRepository(db_session)
    project = repo.create(name="Valid Project")

    updated = repo.update(project.id, invalid_field="Should be ignored")
    assert updated.id == project.id
    assert updated.name == "Valid Project"
    assert not hasattr(updated, "invalid_field")

def test_update_project_with_none_value_does_not_overwrite(db_session):
    repo = ProjectRepository(db_session)
    project = repo.create(name="Original Name")

    updated = repo.update(project.id, name=None)
    assert updated.id == project.id
    assert updated.name == "Original Name"
