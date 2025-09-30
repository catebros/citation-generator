import pytest
import json
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.base import Base
from models.citation import Citation

@pytest.fixture(scope="function")
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    yield session
    session.close()

@pytest.fixture
def sample_book_citation(db_session):
    citation = Citation(
        type="book",
        title="The Great Book",
        authors=json.dumps(["John Smith", "Alice Doe"]),
        year=2023,
        publisher="Academic Press",
        place="New York",
        edition=2
    )
    db_session.add(citation)
    db_session.commit()
    db_session.refresh(citation)
    return citation

@pytest.fixture
def sample_article_citation(db_session):
    citation = Citation(
        type="article",
        title="Research Findings",
        authors=json.dumps(["Mary Johnson", "Kevin Brown", "Robert Wilson"]),
        year=2022,
        journal="Science Journal",
        volume=45,
        issue="3",
        pages="123-145",
        doi="10.1234/science.2022"
    )
    db_session.add(citation)
    db_session.commit()
    db_session.refresh(citation)
    return citation

@pytest.fixture
def sample_website_citation(db_session):
    citation = Citation(
        type="website",
        title="Online Resource",
        authors=json.dumps(["Web Author"]),
        year=2024,
        publisher="Example Website",
        url="https://example.com/resource",
        access_date="2024-01-15"
    )
    db_session.add(citation)
    db_session.commit()
    db_session.refresh(citation)
    return citation

@pytest.fixture
def sample_thesis_citation(db_session):
    citation = Citation(
        type="report",
        title="Annual Report on Climate Change",
        authors=json.dumps(["Sam Graduate"]),
        year=2021,
        publisher="Environmental Research Institute",
        url="https://example.org/climate-report-2021"
    )
    db_session.add(citation)
    db_session.commit()
    db_session.refresh(citation)
    return citation

def test_generate_citation_default_apa_format(sample_book_citation):
    """Test that generate_citation() defaults to APA format."""
    result = sample_book_citation.generate_citation()
    expected = "Smith, J. & Doe, A. (2023). *The Great Book* (2nd ed.). Academic Press."
    assert result == expected

def test_generate_citation_explicit_apa_format(sample_book_citation):
    """Test that generate_citation('apa') works correctly."""
    result = sample_book_citation.generate_citation("apa")
    expected = "Smith, J. & Doe, A. (2023). *The Great Book* (2nd ed.). Academic Press."
    assert result == expected

def test_generate_citation_unsupported_format_raises_error(sample_book_citation):
    """Test that unsupported formats raise ValueError."""
    with pytest.raises(ValueError) as exc_info:
        sample_book_citation.generate_citation("mla")
    assert "Unsupported format: mla" in str(exc_info.value)

def test_get_authors_list_valid_json(sample_article_citation):
    """Test parsing valid JSON authors."""
    authors = sample_article_citation._get_authors_list()
    expected = ["Mary Johnson", "Kevin Brown", "Robert Wilson"]
    assert authors == expected

def test_get_authors_list_empty_authors(db_session):
    """Test handling of empty authors field."""
    citation = Citation(
        type="book",
        title="Test Book",
        authors="",
        year=2023,
        publisher="Test Publisher"
    )
    authors = citation._get_authors_list()
    assert authors == []

def test_get_authors_list_none_authors(db_session):
    """Test handling of None authors field."""
    citation = Citation(
        type="book",
        title="Test Book",
        authors=None,
        year=2023,
        publisher="Test Publisher"
    )
    authors = citation._get_authors_list()
    assert authors == []

def test_get_authors_list_invalid_json_fallback(db_session):
    """Test fallback when authors is not valid JSON."""
    citation = Citation(
        type="book",
        title="Test Book",
        authors="Single Author",
        year=2023,
        publisher="Test Publisher"
    )
    authors = citation._get_authors_list()
    assert authors == ["Single Author"]

def test_format_authors_apa_single_author():
    """Test APA formatting for single author."""
    citation = Citation(type="book", title="Test", authors="", year=2023)
    result = citation._format_authors_apa(["John Smith"])
    assert result == "Smith, J."

def test_format_authors_apa_two_authors():
    """Test APA formatting for two authors."""
    citation = Citation(type="book", title="Test", authors="", year=2023)
    result = citation._format_authors_apa(["John Smith", "Jane Doe"])
    assert result == "Smith, J. & Doe, J."

def test_format_authors_apa_three_or_more_authors():
    """Test APA formatting for three or more authors."""
    citation = Citation(type="book", title="Test", authors="", year=2023)
    result = citation._format_authors_apa(["John Smith", "Jane Doe", "Bob Brown"])
    assert result == "Smith, J., Doe, J., & Brown, B."

def test_format_authors_apa_empty_list():
    """Test APA formatting for empty authors list."""
    citation = Citation(type="book", title="Test", authors="", year=2023)
    result = citation._format_authors_apa([])
    assert result == ""

def test_generate_apa_book_complete_data(sample_book_citation):
    """Test APA book citation with all fields."""
    result = sample_book_citation.generate_citation("apa")
    expected = "Smith, J. & Doe, A. (2023). *The Great Book* (2nd ed.). Academic Press."
    assert result == expected

def test_generate_apa_book_minimal_data(db_session):
    """Test APA book citation with minimal required fields."""
    citation = Citation(
        type="book",
        title="Simple Book",
        authors=json.dumps(["A Author"]),
        year=2023,
        publisher="Publisher"
    )
    result = citation.generate_citation("apa")
    expected = "Author, A. (2023). *Simple Book*. Publisher."
    assert result == expected

def test_generate_apa_book_first_edition_ignored(db_session):
    """Test that 1st edition is not included in APA citation."""
    citation = Citation(
        type="book",
        title="First Edition Book",
        authors=json.dumps(["A Author"]),
        year=2023,
        publisher="Publisher",
        edition=1
    )
    result = citation.generate_citation("apa")
    expected = "Author, A. (2023). *First Edition Book*. Publisher."
    assert result == expected

def test_generate_apa_article_complete_data(sample_article_citation):
    """Test APA article citation with all fields."""
    result = sample_article_citation.generate_citation("apa")
    expected = "Johnson, M., Brown, K., & Wilson, R. (2022). Research Findings. *Science Journal*, 45(3), 123–145. https://doi.org/10.1234/science.2022"
    assert result == expected

def test_generate_apa_article_without_doi(db_session):
    """Test APA article citation without DOI."""
    citation = Citation(
        type="article",
        title="Article Without DOI",
        authors=json.dumps(["A Author"]),
        year=2023,
        journal="Test Journal",
        volume=1,
        issue="2",
        pages="10-20"
    )
    result = citation.generate_citation("apa")
    expected = "Author, A. (2023). Article Without DOI. *Test Journal*, 1(2), 10–20."
    assert result == expected

def test_generate_apa_article_without_issue(db_session):
    """Test APA article citation without issue number."""
    citation = Citation(
        type="article",
        title="Article Without Issue",
        authors=json.dumps(["A Author"]),
        year=2023,
        journal="Test Journal",
        volume=1,
        pages="10-20"
    )
    result = citation.generate_citation("apa")
    expected = "Author, A. (2023). Article Without Issue. *Test Journal*, 1, 10–20."
    assert result == expected

def test_generate_apa_website_complete_data(sample_website_citation):
    """Test APA website citation with all fields."""
    result = sample_website_citation.generate_citation("apa")
    expected = "Author, W. (2024). Online Resource. *Example Website*. https://example.com/resource"
    assert result == expected

def test_generate_apa_website_minimal_data(db_session):
    """Test APA website citation with minimal fields."""
    citation = Citation(
        type="website",
        title="Website Title",
        authors=json.dumps(["Web Author"]),
        year=2024,
        publisher="Sample Site",
        url="https://example.com"
    )
    result = citation.generate_citation("apa")
    expected = "Author, W. (2024). Website Title. *Sample Site*. https://example.com"
    assert result == expected

def test_generate_apa_report_complete_data(sample_thesis_citation):
    """Test APA report citation with all fields."""
    result = sample_thesis_citation.generate_citation("apa")
    expected = "Graduate, S. (2021). *Annual Report on Climate Change* (report). Environmental Research Institute. https://example.org/climate-report-2021"
    assert result == expected

def test_generate_apa_report_without_url(db_session):
    """Test APA report citation without URL."""
    citation = Citation(
        type="report",
        title="Technical Report",
        authors=json.dumps(["M Student"]),
        year=2023,
        publisher="Tech Research Corp"
    )
    result = citation.generate_citation("apa")
    expected = "Student, M. (2023). *Technical Report* (report). Tech Research Corp."
    assert result == expected

def test_generate_apa_citation_missing_fields_handled_gracefully(db_session):
    """Test that missing fields are handled gracefully."""
    citation = Citation(
        type="book",
        title="Incomplete Book",
        authors=json.dumps([]),
        year=None,
        publisher=None
    )
    result = citation.generate_citation("apa")
    expected = "(n.d.). *Incomplete Book*."
    assert result == expected

def test_generate_apa_citation_unsupported_type(db_session):
    """Test handling of unsupported citation types."""
    citation = Citation(
        type="unknown_type",
        title="Unknown Type",
        authors=json.dumps(["Author, A."]),
        year=2023
    )
    result = citation.generate_citation("apa")
    expected = "Unsupported citation type: unknown_type"
    assert result == expected

def test_generate_apa_book_no_authors(db_session):
    """Test APA book citation with no authors."""
    citation = Citation(
        type="book",
        title="Authorless Book",
        authors=json.dumps([]),
        year=2023,
        publisher="Anonymous Press"
    )
    result = citation.generate_citation("apa")
    expected = "(2023). *Authorless Book*. Anonymous Press."
    assert result == expected

def test_generate_apa_article_no_volume_or_pages(db_session):
    """Test APA article citation without volume or pages."""
    citation = Citation(
        type="article",
        title="Basic Article",
        authors=json.dumps(["A Author"]),
        year=2023,
        journal="Simple Journal"
    )
    result = citation.generate_citation("apa")
    expected = "Author, A. (2023). Basic Article. *Simple Journal*."
    assert result == expected

def test_generate_apa_website_no_url(db_session):
    """Test APA website citation without URL."""
    citation = Citation(
        type="website",
        title="Website Without URL",
        authors=json.dumps(["A Author"]),
        year=2023,
        publisher="Test Site"
    )
    result = citation.generate_citation("apa")
    expected = "Author, A. (2023). Website Without URL. *Test Site*."
    assert result == expected

def test_citation_model_integration_with_database(db_session):
    """Test that citation model works properly with database operations."""
    citation_data = {
        "type": "book",
        "title": "Database Test Book",
        "authors": json.dumps(["DB Author"]),
        "year": 2023,
        "publisher": "DB Publisher"
    }
    
    citation = Citation(**citation_data)
    db_session.add(citation)
    db_session.commit()
    db_session.refresh(citation)
    
    # Test that the citation can generate APA format after database operations
    result = citation.generate_citation("apa")
    expected = "Author, D. (2023). *Database Test Book*. DB Publisher."
    assert result == expected
    
    # Test that we can retrieve and use the citation
    retrieved = db_session.query(Citation).filter(Citation.id == citation.id).first()
    assert retrieved is not None
    assert retrieved.generate_citation("apa") == expected
