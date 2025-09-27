import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.base import Base
from models.citation import Citation
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

def test_create_citation(db_session):
    repo = CitationRepository(db_session)

    new_citation = repo.create(
        type="book",
        title="AI Research",
        authors=["John Smith", "Maria Lopez"],
        year=2020
    )

    assert new_citation.id is not None
    assert new_citation.title == "AI Research"
    assert "John Smith" in new_citation.authors

def test_get_citation_by_id(db_session):
    repo = CitationRepository(db_session)

    created = repo.create(
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
        type="book",
        title="AI Foundations",
        authors=["Alan Turing"],
        year=1950
    )
    citation2 = repo.create(
        type="article",
        title="Neural Nets",
        authors=["Geoff Hinton"],
        year=1986
    )

    db_session.add(ProjectCitation(project_id=project.id, citation_id=citation1.id))
    db_session.add(ProjectCitation(project_id=project.id, citation_id=citation2.id))
    db_session.commit()

    results = repo.get_all_by_project(project.id)

    assert len(results) == 2
    titles = [c.title for c in results]
    assert "AI Foundations" in titles
    assert "Neural Nets" in titles

def test_get_all_by_project_empty(db_session):
    repo = CitationRepository(db_session)

    results = repo.get_all_by_project(999)

    assert results == []
