import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.base import Base
from models.project import Project
from models.project_citation import ProjectCitation
from repositories.citation_repo import CitationRepository
from repositories.project_repo import ProjectRepository

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

def test_get_citation_by_id(db_session):
    repo = CitationRepository(db_session)

    project = Project(name="Test Project")
    db_session.add(project)
    db_session.commit()
    db_session.refresh(project)

    created = repo.create(
        project_id=project.id,
        type="article",
        title="Deep Learning Advances",
        authors=["Jane Doe"],
        year=2021
    )

    fetched = repo.get_by_id(created.id)

    assert fetched is not None
    assert fetched.id == created.id
    assert fetched.title == "Deep Learning Advances"
    assert "Jane Doe" in fetched.authors

def test_get_citation_by_id_not_found(db_session):
    repo = CitationRepository(db_session)

    fetched = repo.get_by_id(999)

    assert fetched is None

def test_delete_citation_single_project(db_session):
    repo = CitationRepository(db_session)

    project = Project(name="Project A")
    db_session.add(project)
    db_session.commit()
    db_session.refresh(project)

    citation = repo.create(
        project_id=project.id,
        type="book",
        title="Book 1",
        authors=["Author A"],
        year=2000,
    )

    ok = repo.delete(citation.id, project_id=project.id)
    assert ok is True
    assert repo.get_by_id(citation.id) is None

    assoc = (
        db_session.query(ProjectCitation)
        .filter(ProjectCitation.citation_id == citation.id)
        .first()
    )
    assert assoc is None

def test_delete_citation_multiple_projects(db_session):
    repo = CitationRepository(db_session)

    project1 = Project(name="Project A")
    project2 = Project(name="Project B")
    db_session.add_all([project1, project2])
    db_session.commit()
    db_session.refresh(project1)
    db_session.refresh(project2)

    citation = repo.create(
        project_id=project1.id,
        type="article",
        title="Shared Citation",
        authors=["Author B"],
        year=2010,
    )

    repo.create(
        project_id=project2.id,
        type="article",
        title="Shared Citation",
        authors=["Author B"],
        year=2010,
    )

    ok = repo.delete(citation.id, project_id=project1.id)
    assert ok is True

    still_exists = repo.get_by_id(citation.id)
    assert still_exists is not None

    assoc1 = (
        db_session.query(ProjectCitation)
        .filter(ProjectCitation.project_id == project1.id, ProjectCitation.citation_id == citation.id)
        .first()
    )
    assoc2 = (
        db_session.query(ProjectCitation)
        .filter(ProjectCitation.project_id == project2.id, ProjectCitation.citation_id == citation.id)
        .first()
    )
    assert assoc1 is None
    assert assoc2 is not None

def test_delete_orphan_citation(db_session):
    repo = CitationRepository(db_session)

    citation = repo.create(
        project_id=1,  
        type="book",
        title="Orphan Citation",
        authors=["Author C"],
        year=1999,
    )

    db_session.query(ProjectCitation).delete()  
    db_session.commit()

    ok = repo.delete(citation.id)
    assert ok is True
    assert repo.get_by_id(citation.id) is None

def test_update_citation(db_session):
    repo = CitationRepository(db_session)

    project = Project(name="Update Project")
    db_session.add(project)
    db_session.commit()
    db_session.refresh(project)

    citation = repo.create(
        project_id=project.id,
        type="book",
        title="Old Title",
        authors=["Jane Doe"],
        year=2000
    )

    updated = repo.update(citation.id, project_id=project.id, title="New Title", year=2021)

    assert updated is not None
    assert updated.title == "New Title"
    assert updated.year == 2021

def test_update_citation_title_and_year(db_session):
    repo = CitationRepository(db_session)

    project = Project(name="Project TY")
    db_session.add(project)
    db_session.commit()
    db_session.refresh(project)

    c = repo.create(project_id=project.id, type="book", title="Old", authors=["X"], year=1990)

    updated = repo.update(c.id, project_id=project.id, title="New", year=2000)
    assert updated.title == "New"
    assert updated.year == 2000

def test_update_citation_authors(db_session):
    repo = CitationRepository(db_session)

    project = Project(name="Project Authors")
    db_session.add(project)
    db_session.commit()
    db_session.refresh(project)

    c = repo.create(project_id=project.id, type="article", title="Authored", authors=["Y"], year=2001)

    updated = repo.update(c.id, project_id=project.id, authors=["Y", "Z"])
    assert "Y" in updated.authors
    assert "Z" in updated.authors

def test_update_citation_not_found(db_session):
    repo = CitationRepository(db_session)

    project = Project(name="Test Project")
    db_session.add(project)
    db_session.commit()
    db_session.refresh(project)

    result = repo.update(999, project_id=project.id, title="Doesn't matter")

    assert result is None

def test_update_citation_with_project_id_required(db_session):
    repo = CitationRepository(db_session)
    
    project = Project(name="Test Project")
    db_session.add(project)
    db_session.commit()
    db_session.refresh(project)
    
    citation = repo.create(
        project_id=project.id,
        type="book",
        title="Test Title",
        authors=["Author"],
        year=2020
    )
    
    with pytest.raises(ValueError, match="project_id is required"):
        repo.update(citation.id, project_id=None, title="New Title")

def test_update_citation_merges_with_existing_identical(db_session):
    repo = CitationRepository(db_session)
    project_repo = ProjectRepository(db_session)
    project = Project(name="Merge Project")
    db_session.add(project)
    db_session.commit()
    db_session.refresh(project)
    
    existing_citation = repo.create(
        project_id=project.id,
        type="article",
        title="Existing Article",
        authors=["Author A"],
        year=2020
    )
    
    citation_to_update = repo.create(
        project_id=project.id,
        type="book",
        title="Book to Update",
        authors=["Author B"],
        year=2021
    )
    
    updated = repo.update(
        citation_to_update.id,
        project_id=project.id,
        type="article",
        title="Existing Article",
        authors=["Author A"],
        year=2020
    )
    
    assert updated.id == existing_citation.id
    
    assert repo.get_by_id(citation_to_update.id) is None
    
    all_citations = project_repo.get_all_by_project(project.id)
    assert len(all_citations) == 1

def test_update_citation_multiple_projects_creates_new(db_session):
    """Test que si una cita está en múltiples proyectos y se actualiza, se crea una nueva"""
    repo = CitationRepository(db_session)
    project_repo = ProjectRepository(db_session)
    project1 = Project(name="Project 1")
    project2 = Project(name="Project 2")
    db_session.add_all([project1, project2])
    db_session.commit()
    db_session.refresh(project1)
    db_session.refresh(project2)
    
    original_citation = repo.create(
        project_id=project1.id,
        type="article",
        title="Shared Article",
        authors=["Shared Author"],
        year=2020
    )
    
    assoc = ProjectCitation(project_id=project2.id, citation_id=original_citation.id)
    db_session.add(assoc)
    db_session.commit()
    
    updated = repo.update(
        original_citation.id,
        project_id=project1.id,
        title="Updated Title"
    )
    
    assert updated.id != original_citation.id
    assert updated.title == "Updated Title"
    
    project1_citations = project_repo.get_all_by_project(project1.id) 
    assert len(project1_citations) == 1
    assert project1_citations[0].title == "Updated Title"

    project2_citations = project_repo.get_all_by_project(project2.id)  
    assert len(project2_citations) == 1
    assert project2_citations[0].title == "Shared Article"

def test_update_citation_single_project_modifies_in_place(db_session):
    repo = CitationRepository(db_session)
    
    project = Project(name="Single Project")
    db_session.add(project)
    db_session.commit()
    db_session.refresh(project)
    
    citation = repo.create(
        project_id=project.id,
        type="book",
        title="Original Title",
        authors=["Original Author"],
        year=2020
    )
    
    original_id = citation.id
    
    updated = repo.update(
        citation.id,
        project_id=project.id,
        title="Modified Title",
        year=2021
    )
    
    assert updated.id == original_id
    assert updated.title == "Modified Title"
    assert updated.year == 2021
    assert "Original Author" in updated.authors  

def test_update_citation_with_all_fields(db_session):
    repo = CitationRepository(db_session)
    
    project = Project(name="Complete Project")
    db_session.add(project)
    db_session.commit()
    db_session.refresh(project)
    
    citation = repo.create(
        project_id=project.id,
        type="book",
        title="Basic Book",
        authors=["Author"],
        year=2020
    )
    
    updated = repo.update(
        citation.id,
        project_id=project.id,
        type="article",
        title="Complete Article",
        authors=["Author A", "Author B"],
        year=2023,
        publisher="Academic Press",
        journal="Science Journal",
        volume="42",
        issue="3",
        pages="123-145",
        doi="10.1000/test.doi",
        url="https://example.com",
        access_date="2023-01-01",
        place="New York",
        edition="2nd"
    )
    
    assert updated.type == "article"
    assert updated.title == "Complete Article"
    assert "Author A" in updated.authors
    assert "Author B" in updated.authors
    assert updated.year == 2023
    assert updated.publisher == "Academic Press"
    assert updated.journal == "Science Journal"
    assert updated.volume == "42"
    assert updated.issue == "3"
    assert updated.pages == "123-145"
    assert updated.doi == "10.1000/test.doi"
    assert updated.url == "https://example.com"
    assert updated.access_date == "2023-01-01"
    assert updated.place == "New York"
    assert updated.edition == "2nd"

def test_update_citation_ignores_none_values(db_session):
    repo = CitationRepository(db_session)
    
    project = Project(name="None Test Project")
    db_session.add(project)
    db_session.commit()
    db_session.refresh(project)
    
    citation = repo.create(
        project_id=project.id,
        type="book",
        title="Original Title",
        authors=["Author"],
        year=2020,
        publisher="Original Publisher"
    )
    
    updated = repo.update(
        citation.id,
        project_id=project.id,
        title="New Title",
        publisher=None, 
        journal=None    
    )
    
    assert updated.title == "New Title"
    assert updated.publisher == "Original Publisher" 
    assert updated.journal is None  

def test_update_citation_with_invalid_attributes(db_session):
    repo = CitationRepository(db_session)
    
    project = Project(name="Invalid Attr Project")
    db_session.add(project)
    db_session.commit()
    db_session.refresh(project)
    
    citation = repo.create(
        project_id=project.id,
        type="article",
        title="Test Article",
        authors=["Author"],
        year=2020
    )
    
    updated = repo.update(
        citation.id,
        project_id=project.id,
        title="Updated Title",
        invalid_field="This should be ignored"
    )
    
    assert updated.title == "Updated Title"
    assert not hasattr(updated, 'invalid_field')