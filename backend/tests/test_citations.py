import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.base import Base
from models.project import Project
from models.project_citation import ProjectCitation
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

def test_get_all_by_project(db_session):
    repo = CitationRepository(db_session)

    project = Project(name="Thesis on AI")
    db_session.add(project)
    db_session.commit()
    db_session.refresh(project)

    citation1 = repo.create(
        project_id=project.id,
        type="book",
        title="AI Foundations",
        authors=["Alan Turing"],
        year=1950
    )
    citation2 = repo.create(
        project_id=project.id,
        type="article",
        title="Neural Nets",
        authors=["Geoff Hinton"],
        year=1986
    )

    results = repo.get_all_by_project(project.id)

    assert len(results) == 2
    titles = [c.title for c in results]
    assert "AI Foundations" in titles
    assert "Neural Nets" in titles

def test_get_all_by_project_empty(db_session):
    repo = CitationRepository(db_session)

    results = repo.get_all_by_project(999)

    assert results == []

def test_get_all_by_project_nonexistent_project(db_session):
    repo = CitationRepository(db_session)

    results = repo.get_all_by_project(12345)
    assert results == []

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

    updated = repo.update(citation.id, title="New Title", year=2021)

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

    updated = repo.update(c.id, title="New", year=2000)
    assert updated.title == "New"
    assert updated.year == 2000

def test_update_citation_authors(db_session):
    repo = CitationRepository(db_session)

    project = Project(name="Project Authors")
    db_session.add(project)
    db_session.commit()
    db_session.refresh(project)

    c = repo.create(project_id=project.id, type="article", title="Authored", authors=["Y"], year=2001)

    updated = repo.update(c.id, authors=["Y", "Z"])
    assert "Y" in updated.authors
    assert "Z" in updated.authors

def test_update_citation_not_found(db_session):
    repo = CitationRepository(db_session)

    result = repo.update(999, title="Doesn't matter")

    assert result is None
