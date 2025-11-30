# backend/tests/test_integration_formatter.py
import pytest
from services.citation_service import CitationService
from services.project_service import ProjectService
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models.base import Base


@pytest.fixture(scope="function")
def db_session():
    """Create a fresh in-memory database for each test."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    yield session
    session.close()


@pytest.fixture
def project_service(db_session):
    """Provide a ProjectService instance with test database."""
    return ProjectService(db_session)


@pytest.fixture
def citation_service(db_session):
    """Provide a CitationService instance with test database."""
    return CitationService(db_session)


def test_apa_formatter_with_real_book_citation(project_service, citation_service):
    """Test APA formatter with real book citation from database."""
    project = project_service.create_project({"name": "APA Book Test"})
    citation = citation_service.create_citation(
        project.id,
        {
            "type": "book",
            "title": "The Psychology of Learning",
            "authors": ["John Smith", "Jane Doe"],
            "year": 2023,
            "publisher": "Academic Press",
            "place": "New York",
            "edition": 2
        }
    )

    formatted = citation_service.format_citation(citation, "apa")

    assert "Smith" in formatted and "Doe" in formatted
    assert "2023" in formatted
    assert "Academic Press" in formatted


def test_mla_formatter_with_real_book_citation(project_service, citation_service):
    """Test MLA formatter with real book citation from database."""
    project = project_service.create_project({"name": "MLA Book Test"})
    citation = citation_service.create_citation(
        project.id,
        {
            "type": "book",
            "title": "Modern Research Methods",
            "authors": ["Mary Johnson", "Robert Williams"],
            "year": 2023,
            "publisher": "University Press",
            "place": "Boston",
            "edition": 3
        }
    )

    formatted = citation_service.format_citation(citation, "mla")

    assert "Johnson" in formatted and "Williams" in formatted
    assert "Modern Research Methods" in formatted
    assert "University Press" in formatted
    assert "2023" in formatted


def test_apa_formatter_with_real_article_citation(project_service, citation_service):
    """Test APA formatter with real article citation from database."""
    project = project_service.create_project({"name": "APA Article Test"})
    citation = citation_service.create_citation(
        project.id,
        {
            "type": "article",
            "title": "Advances in Machine Learning",
            "authors": ["Li Chen", "Raj Kumar"],
            "year": 2023,
            "journal": "Journal of Artificial Intelligence",
            "volume": 15,
            "issue": "3",
            "pages": "45-67",
            "doi": "10.1000/jai.2023.15.3.45"
        }
    )

    formatted = citation_service.format_citation(citation, "apa")

    assert "Chen" in formatted and "Kumar" in formatted
    assert "2023" in formatted
    assert "Journal of Artificial Intelligence" in formatted
    assert "15" in formatted


def test_mla_formatter_with_real_article_citation(project_service, citation_service):
    """Test MLA formatter with real article citation from database."""
    project = project_service.create_project({"name": "MLA Article Test"})
    citation = citation_service.create_citation(
        project.id,
        {
            "type": "article",
            "title": "Climate Change and Agriculture",
            "authors": ["Maria Garcia"],
            "year": 2023,
            "journal": "Environmental Studies Quarterly",
            "volume": 42,
            "issue": "2",
            "pages": "100-125",
            "doi": "10.5000/esq.2023.42.2.100"
        }
    )

    formatted = citation_service.format_citation(citation, "mla")

    assert "Garcia" in formatted
    assert "Climate Change and Agriculture" in formatted
    assert "Environmental Studies Quarterly" in formatted
    assert "2023" in formatted


def test_bibliography_generation_apa_integration(project_service, citation_service):
    """Test complete APA bibliography generation through service layer."""
    project = project_service.create_project({"name": "APA Bibliography Test"})

    citation_service.create_citation(
        project.id,
        {
            "type": "book",
            "title": "Research Fundamentals",
            "authors": ["Paul Anderson"],
            "year": 2022,
            "publisher": "Research Press",
            "place": "Chicago",
            "edition": 1
        }
    )

    citation_service.create_citation(
        project.id,
        {
            "type": "article",
            "title": "Data Analysis Techniques",
            "authors": ["Sarah Brown", "David Lee"],
            "year": 2023,
            "journal": "Statistics Review",
            "volume": 8,
            "issue": "1",
            "pages": "12-34",
            "doi": "10.2000/sr.2023.8.1.12"
        }
    )

    bibliography = project_service.generate_bibliography_by_project(
        project.id, format_type="apa"
    )

    assert bibliography["citation_count"] == 2
    assert bibliography["format_type"] == "apa"
    assert len(bibliography["bibliography"]) == 2

    bib_text = " ".join(bibliography["bibliography"])
    assert "Anderson" in bib_text
    assert "Brown" in bib_text and "Lee" in bib_text


def test_bibliography_generation_mla_integration(project_service, citation_service):
    """Test complete MLA bibliography generation through service layer."""
    project = project_service.create_project({"name": "MLA Bibliography Test"})

    citation_service.create_citation(
        project.id,
        {
            "type": "book",
            "title": "Literary Analysis",
            "authors": ["Michael Thompson"],
            "year": 2021,
            "publisher": "Literary Press",
            "place": "London",
            "edition": 2
        }
    )

    bibliography = project_service.generate_bibliography_by_project(
        project.id, format_type="mla"
    )

    assert bibliography["citation_count"] == 1
    assert bibliography["format_type"] == "mla"
    assert len(bibliography["bibliography"]) == 1
    assert "Thompson" in bibliography["bibliography"][0]


def test_format_switching_same_citations(project_service, citation_service):
    """Test switching between APA and MLA formats for same citations."""
    project = project_service.create_project({"name": "Format Switch Test"})

    citation_service.create_citation(
        project.id,
        {
            "type": "book",
            "title": "Scientific Writing",
            "authors": ["Alice Baker", "Bob Clark"],
            "year": 2023,
            "publisher": "Science Press",
            "place": "San Francisco",
            "edition": 1
        }
    )

    apa_bib = project_service.generate_bibliography_by_project(
        project.id, format_type="apa"
    )
    mla_bib = project_service.generate_bibliography_by_project(
        project.id, format_type="mla"
    )

    assert apa_bib["citation_count"] == 1
    assert mla_bib["citation_count"] == 1
    assert apa_bib["bibliography"] != mla_bib["bibliography"]


def test_formatter_with_website_citation(project_service, citation_service):
    """Test formatters handle website citations correctly."""
    project = project_service.create_project({"name": "Website Test"})
    citation = citation_service.create_citation(
        project.id,
        {
            "type": "website",
            "title": "Web Development Best Practices",
            "authors": ["Carlos Martinez"],
            "year": 2023,
            "publisher": "DevHub",
            "url": "https://example.com/webdev",
            "access_date": "2023-12-01"
        }
    )

    apa_formatted = citation_service.format_citation(citation, "apa")
    mla_formatted = citation_service.format_citation(citation, "mla")

    assert "example.com" in apa_formatted or "https://example.com" in apa_formatted
    assert "example.com" in mla_formatted or "https://example.com" in mla_formatted
    assert "Martinez" in apa_formatted and "Martinez" in mla_formatted


def test_empty_bibliography_formatting(project_service):
    """Test bibliography generation with no citations."""
    project = project_service.create_project({"name": "Empty Project"})

    apa_bib = project_service.generate_bibliography_by_project(
        project.id, format_type="apa"
    )
    mla_bib = project_service.generate_bibliography_by_project(
        project.id, format_type="mla"
    )

    assert apa_bib["citation_count"] == 0
    assert mla_bib["citation_count"] == 0
    assert len(apa_bib["bibliography"]) == 0
    assert len(mla_bib["bibliography"]) == 0


def test_bibliography_sorting(project_service, citation_service):
    """Test that bibliography entries are properly sorted."""
    project = project_service.create_project({"name": "Sorting Test"})

    citation_service.create_citation(
        project.id,
        {
            "type": "book",
            "title": "Zebra Studies",
            "authors": ["Zoe Zimmerman"],
            "year": 2023,
            "publisher": "Wildlife Press",
            "place": "Denver",
            "edition": 1
        }
    )

    citation_service.create_citation(
        project.id,
        {
            "type": "book",
            "title": "Ant Colonies",
            "authors": ["Amy Anderson"],
            "year": 2023,
            "publisher": "Nature Press",
            "place": "Seattle",
            "edition": 1
        }
    )

    bibliography = project_service.generate_bibliography_by_project(
        project.id, format_type="apa"
    )

    assert len(bibliography["bibliography"]) == 2
    # Check if sorted alphabetically by author
    bib_list = bibliography["bibliography"]
    assert "Anderson" in bib_list[0]
    assert "Zimmerman" in bib_list[1]


def test_updated_citation_reflects_in_bibliography(project_service, citation_service):
    """Test that updating citation reflects in generated bibliography."""
    project = project_service.create_project({"name": "Update Test"})
    citation = citation_service.create_citation(
        project.id,
        {
            "type": "book",
            "title": "Original Title",
            "authors": ["Original Author"],
            "year": 2022,
            "publisher": "Old Publisher",
            "place": "Old City",
            "edition": 1
        }
    )

    initial_bib = project_service.generate_bibliography_by_project(
        project.id, format_type="apa"
    )
    # Title may be in sentence case (lowercase)
    assert "Original title" in initial_bib["bibliography"][0] or "Original Title" in initial_bib["bibliography"][0]

    citation_service.update_citation(
        citation.id,
        project.id,
        {"title": "Updated Title", "year": 2023}
    )

    updated_bib = project_service.generate_bibliography_by_project(
        project.id, format_type="apa"
    )

    # Title may be in sentence case (lowercase)
    assert "Updated title" in updated_bib["bibliography"][0] or "Updated Title" in updated_bib["bibliography"][0]
    assert "2023" in updated_bib["bibliography"][0]
