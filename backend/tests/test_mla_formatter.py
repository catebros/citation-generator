import pytest
import json
from models.citation import Citation
from services.formatters.mla_formatter import MLAFormatter


def test_mla_book_single_author():
    """Test MLA book citation with single author."""
    citation = Citation(
        type="book",
        title="To Kill a Mockingbird",
        authors=json.dumps(["Harper Lee"]),
        year=1960,
        publisher="J.B. Lippincott & Co."
    )
    formatter = MLAFormatter(citation)
    result = formatter._format_book(formatter._format_authors(formatter._get_authors_list()))
    expected = "Lee, Harper. *To Kill a Mockingbird*. J.B. Lippincott & Co., 1960."
    assert result == expected

def test_mla_book_two_authors():
    """Test MLA book citation with two authors."""
    citation = Citation(
        type="book",
        title="The Great Book",
        authors=json.dumps(["John Smith", "Alice Doe"]),
        year=2023,
        publisher="Academic Press"
    )
    formatter = MLAFormatter(citation)
    result = formatter._format_book(formatter._format_authors(formatter._get_authors_list()))
    expected = "Smith, John, and Alice Doe. *The Great Book*. Academic Press, 2023."
    assert result == expected

def test_mla_book_three_authors():
    """Test MLA book citation with three authors."""
    citation = Citation(
        type="book",
        title="Research Methods",
        authors=json.dumps(["John Smith", "Alice Doe", "Bob Johnson"]),
        year=2022,
        publisher="Research Press"
    )
    formatter = MLAFormatter(citation)
    result = formatter._format_book(formatter._format_authors(formatter._get_authors_list()))
    expected = "Smith, John, Alice Doe, and Bob Johnson. *Research Methods*. Research Press, 2022."
    assert result == expected

def test_mla_book_with_edition():
    """Test MLA book citation with edition."""
    citation = Citation(
        type="book",
        title="Programming Fundamentals",
        authors=json.dumps(["Jane Developer"]),
        year=2023,
        publisher="Tech Books",
        edition=3
    )
    formatter = MLAFormatter(citation)
    result = formatter._format_book(formatter._format_authors(formatter._get_authors_list()))
    expected = "Developer, Jane. *Programming Fundamentals*. 3rd ed., Tech Books, 2023."
    assert result == expected

def test_mla_book_first_edition_ignored():
    """Test MLA book citation ignores first edition."""
    citation = Citation(
        type="book",
        title="First Edition Book",
        authors=json.dumps(["Author Name"]),
        year=2023,
        publisher="Publisher",
        edition=1
    )
    formatter = MLAFormatter(citation)
    result = formatter._format_book(formatter._format_authors(formatter._get_authors_list()))
    expected = "Name, Author. *First Edition Book*. Publisher, 2023."
    assert result == expected

def test_mla_article_complete_data():
    """Test MLA article citation with complete data."""
    citation = Citation(
        type="article",
        title="Climate Change Effects",
        authors=json.dumps(["Jane Smith", "John Doe"]),
        year=2023,
        journal="Environmental Science Today",
        volume=45,
        issue="2",
        pages="123-145",
        doi="10.1234/est.2023.45.2.123"
    )
    formatter = MLAFormatter(citation)
    result = formatter._format_article(formatter._format_authors(formatter._get_authors_list()))
    expected = 'Smith, Jane, and John Doe. "Climate Change Effects." *Environmental Science Today*, vol. 45, no. 2, 2023, pp. 123–145. https://doi.org/10.1234/est.2023.45.2.123.'
    assert result == expected

def test_mla_article_without_doi():
    """Test MLA article citation without DOI."""
    citation = Citation(
        type="article",
        title="Research Study",
        authors=json.dumps(["Alice Johnson"]),
        year=2022,
        journal="Science Journal",
        volume=30,
        pages="45-60"
    )
    formatter = MLAFormatter(citation)
    result = formatter._format_article(formatter._format_authors(formatter._get_authors_list()))
    expected = 'Johnson, Alice. "Research Study." *Science Journal*, vol. 30, 2022, pp. 45–60.'
    assert result == expected

def test_mla_article_without_issue():
    """Test MLA article citation without issue number."""
    citation = Citation(
        type="article",
        title="Simple Study",
        authors=json.dumps(["Bob Writer"]),
        year=2023,
        journal="Research Today",
        volume=15,
        pages="10-20"
    )
    formatter = MLAFormatter(citation)
    result = formatter._format_article(formatter._format_authors(formatter._get_authors_list()))
    expected = 'Writer, Bob. "Simple Study." *Research Today*, vol. 15, 2023, pp. 10–20.'
    assert result == expected

def test_mla_website_complete_data():
    """Test MLA website citation with complete data."""
    citation = Citation(
        type="website",
        title="Understanding Climate Change",
        authors=json.dumps(["Environmental Team"]),
        year=2023,
        publisher="Climate Organization",
        url="https://example.org/climate-change",
        access_date="15 Mar. 2023"
    )
    formatter = MLAFormatter(citation)
    result = formatter._format_website(formatter._format_authors(formatter._get_authors_list()))
    expected = 'Team, Environmental. "Understanding Climate Change." *Climate Organization*, 2023, https://example.org/climate-change.'
    assert result == expected

def test_mla_website_without_author():
    """Test MLA website citation without author."""
    citation = Citation(
        type="website",
        title="News Article",
        authors=json.dumps([]),
        year=2023,
        publisher="News Site",
        url="https://example.org/news",
        access_date="20 Jan. 2023"
    )
    formatter = MLAFormatter(citation)
    result = formatter._format_website(formatter._format_authors(formatter._get_authors_list()))
    expected = '"News Article." *News Site*, 2023, https://example.org/news.'
    assert result == expected

def test_mla_website_without_access_date():
    """Test MLA website citation without access date."""
    citation = Citation(
        type="website",
        title="Online Resource",
        authors=json.dumps(["Web Author"]),
        year=2023,
        publisher="Web Publisher",
        url="https://example.org/resource"
    )
    formatter = MLAFormatter(citation)
    result = formatter._format_website(formatter._format_authors(formatter._get_authors_list()))
    expected = 'Author, Web. "Online Resource." *Web Publisher*, 2023, https://example.org/resource.'
    assert result == expected

def test_mla_report_complete_data():
    """Test MLA report citation with complete data."""
    citation = Citation(
        type="report",
        title="Annual Climate Report",
        authors=json.dumps(["Sarah Graduate"]),
        year=2021,
        publisher="Environmental Research Institute",
        url="https://example.org/climate-report-2021"
    )
    formatter = MLAFormatter(citation)
    result = formatter._format_report(formatter._format_authors(formatter._get_authors_list()))
    expected = "Graduate, Sarah. *Annual Climate Report*. Environmental Research Institute, 2021. https://example.org/climate-report-2021."
    assert result == expected

def test_mla_report_without_url():
    """Test MLA report citation without URL."""
    citation = Citation(
        type="report",
        title="Technical Report",
        authors=json.dumps(["M Student"]),
        year=2023,
        publisher="Tech Research Corp"
    )
    formatter = MLAFormatter(citation)
    result = formatter._format_report(formatter._format_authors(formatter._get_authors_list()))
    expected = "Student, M. *Technical Report*. Tech Research Corp, 2023."
    assert result == expected

def test_mla_format_authors_single():
    """Test MLA author formatting for single author."""
    citation = Citation(
        type="book",
        authors=json.dumps(["John Smith"])
    )
    formatter = MLAFormatter(citation)
    result = formatter._format_authors(formatter._get_authors_list())
    expected = "Smith, John"
    assert result == expected

def test_mla_format_authors_two():
    """Test MLA author formatting for two authors."""
    citation = Citation(
        type="book",
        authors=json.dumps(["John Smith", "Alice Doe"])
    )
    formatter = MLAFormatter(citation)
    result = formatter._format_authors(formatter._get_authors_list())
    expected = "Smith, John, and Alice Doe"
    assert result == expected

def test_mla_format_authors_three_or_more():
    """Test MLA author formatting for three or more authors."""
    citation = Citation(
        type="book",
        authors=json.dumps(["John Smith", "Alice Doe", "Bob Johnson", "Carol White"])
    )
    formatter = MLAFormatter(citation)
    result = formatter._format_authors(formatter._get_authors_list())
    # With 4 authors, MLA now uses et al.
    expected = "Smith, John, et al."
    assert result == expected

def test_mla_format_authors_empty():
    """Test MLA author formatting for empty authors."""
    citation = Citation(
        type="book",
        authors=json.dumps([])
    )
    formatter = MLAFormatter(citation)
    result = formatter._format_authors(formatter._get_authors_list())
    expected = ""
    assert result == expected

def test_mla__normalize_edition_various():
    """Test MLA edition normalization."""
    citation = Citation(type="book")
    formatter = MLAFormatter(citation)
    
    # Test various editions
    assert formatter._normalize_edition(1) == ""  # First edition ignored
    assert formatter._normalize_edition(2) == "2nd ed."
    assert formatter._normalize_edition(3) == "3rd ed."
    assert formatter._normalize_edition(4) == "4th ed."
    assert formatter._normalize_edition(21) == "21st ed."
    assert formatter._normalize_edition(22) == "22nd ed."
    assert formatter._normalize_edition(23) == "23rd ed."
    assert formatter._normalize_edition(24) == "24th ed."
    # Test special cases with teens (should be "th")
    assert formatter._normalize_edition(11) == "11th ed."
    assert formatter._normalize_edition(12) == "12th ed."
    assert formatter._normalize_edition(13) == "13th ed."
    # Test three-digit numbers
    assert formatter._normalize_edition(101) == "101st ed."
    assert formatter._normalize_edition(102) == "102nd ed."
    assert formatter._normalize_edition(103) == "103rd ed."
    assert formatter._normalize_edition(111) == "111th ed."
    assert formatter._normalize_edition(112) == "112th ed."
    assert formatter._normalize_edition(113) == "113th ed."

def test_mla_unsupported_citation_type():
    """Test MLA formatter with unsupported citation type."""
    citation = Citation(
        type="unsupported",
        title="Unknown Type",
        authors=json.dumps(["Author Name"])
    )
    formatter = MLAFormatter(citation)
    
    # MLA formatter returns string for unsupported types instead of raising exception
    result = formatter.format_citation()
    expected = "Unsupported citation type: unsupported"
    assert result == expected

def test_mla_missing_required_fields_handled_gracefully():
    """Test MLA formatter handles missing fields gracefully."""
    citation = Citation(
        type="book",
        title="",  # Empty title
        authors=json.dumps([]),  # No authors
        year=None,  # No year
        publisher=""  # Empty publisher
    )
    formatter = MLAFormatter(citation)
    result = formatter._format_book(formatter._format_authors(formatter._get_authors_list()))
    
    # Should handle missing fields without crashing
    assert isinstance(result, str)
    assert "n.d." in result  # Should show "no date"


# ========== SPECIFIC MISSING TEST CASES ==========

def test_mla_book_with_advanced_edition_in_real_citation():
    """Test MLA book with advanced edition (22nd ed.) integrated in real citation."""
    citation = Citation(
        type="book",
        title="Modern Literary Theory",
        authors=json.dumps(["García, María", "Johnson, Robert"]),
        year=2023,
        publisher="University Press",
        edition=22
    )
    formatter = MLAFormatter(citation)
    result = formatter.format_citation()
    
    assert "22nd ed." in result
    expected = "María, García,, and Johnson, Robert. *Modern Literary Theory*. 22nd ed., University Press, 2023."
    assert result == expected


def test_mla_article_year_none_shows_nd():
    """Test MLA article with year=None shows n.d."""
    citation = Citation(
        type="article",
        title="Undated Research",
        authors=json.dumps(["Smith, John"]),
        year=None,
        journal="Academic Journal",
        volume="15",
        pages="45-60"
    )
    formatter = MLAFormatter(citation)
    result = formatter.format_citation()
    
    assert "n.d." in result
    expected = 'John, Smith,. "Undated Research." *Academic Journal*, vol. 15, n.d., pp. 45–60.'
    assert result == expected


def test_mla_website_year_none_with_valid_access_date():
    """Test MLA website with year=None and valid access_date."""
    citation = Citation(
        type="website",
        title="Online Resource",
        authors=json.dumps(["Web, Author"]),
        year=None,
        publisher="Example Website",
        url="https://example.com/resource",
        access_date="2025-10-02"
    )
    formatter = MLAFormatter(citation)
    result = formatter.format_citation()
    
    assert "Accessed 2 Oct. 2025" in result
    expected = 'Author, Web,. "Online Resource." *Example Website*, https://example.com/resource. Accessed 2 Oct. 2025.'
    assert result == expected


def test_mla_website_year_none_with_invalid_access_date():
    """Test MLA website with year=None and invalid access_date format."""
    citation = Citation(
        type="website",
        title="Another Resource",
        authors=json.dumps(["Digital, Author"]),
        year=None,
        publisher="Test Site",
        url="https://test.com",
        access_date="not-a-date"
    )
    formatter = MLAFormatter(citation)
    result = formatter.format_citation()
    
    assert "Accessed not-a-date" in result
    expected = 'Author, Digital,. "Another Resource." *Test Site*, https://test.com. Accessed not-a-date.'
    assert result == expected


def test_mla_report_year_none_shows_nd():
    """Test MLA report with year=None shows n.d."""
    citation = Citation(
        type="report",
        title="Technical Report",
        authors=json.dumps(["Institute, Research"]),
        year=None,
        publisher="Government Agency"
    )
    formatter = MLAFormatter(citation)
    result = formatter.format_citation()
    
    assert "n.d." in result
    expected = "Research, Institute,. *Technical Report*. Government Agency, n.d.."
    assert result == expected


def test_mla_authors_four_or_more_shows_et_al():
    """Test MLA with 4+ authors shows first author + et al."""
    # Test with 4 authors
    authors_list = ["Smith John", "Doe Jane", "Brown Bob", "Wilson Alice"]
    
    citation = Citation(
        type="book",
        title="Collaborative Work",
        authors=json.dumps(authors_list),
        year=2023,
        publisher="Academic Press"
    )
    formatter = MLAFormatter(citation)
    formatted_authors = formatter._format_authors(authors_list)
    
    # Should show first author + et al.
    assert formatted_authors == "John, Smith, et al."
    
    # Test with 10 authors
    many_authors = [f"Author{i} First{i}" for i in range(1, 11)]
    formatted_many = formatter._format_authors(many_authors)
    assert formatted_many == "First1, Author1, et al."


def test_mla_authors_exactly_three_lists_all():
    """Test MLA with exactly 3 authors lists all authors without et al."""
    authors_list = ["Smith John", "Doe Jane", "Brown Bob"]
    
    citation = Citation(
        type="book",
        title="Three Authors Book",
        authors=json.dumps(authors_list),
        year=2023,
        publisher="Academic Press"
    )
    formatter = MLAFormatter(citation)
    formatted_authors = formatter._format_authors(authors_list)
    
    # Should list all three authors without et al.
    assert "et al." not in formatted_authors
    assert "John, Smith" in formatted_authors
    assert "Doe Jane" in formatted_authors  # Second author format
    assert "Brown Bob" in formatted_authors  # Third author format
    expected = "John, Smith, Doe Jane, and Brown Bob"
    assert formatted_authors == expected
