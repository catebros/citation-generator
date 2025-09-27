import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.base import Base
from models.citation import Citation
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
