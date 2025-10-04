import pytest
import json
from models.citation import Citation
from services.formatters.apa_formatter import APAFormatter

def test_apa_format_authors_single_author():
    """Test APA formatting for single author."""
    citation = Citation(type="book", title="Test", authors="", year=2023)
    formatter = APAFormatter(citation)
    result = formatter._format_authors(["John Smith"])
    assert result == "Smith, J."

def test_apa_format_authors_two_authors():
    """Test APA formatting for two authors."""
    citation = Citation(type="book", title="Test", authors="", year=2023)
    formatter = APAFormatter(citation)
    result = formatter._format_authors(["John Smith", "Jane Doe"])
    assert result == "Smith, J., & Doe, J."

def test_apa_format_authors_three_or_more_authors():
    """Test APA formatting for three or more authors."""
    citation = Citation(type="book", title="Test", authors="", year=2023)
    formatter = APAFormatter(citation)
    result = formatter._format_authors(["John Smith", "Jane Doe", "Bob Brown"])
    assert result == "Smith, J., Doe, J., & Brown, B."

def test_apa_format_authors_empty_list():
    """Test APA formatting for empty authors list."""
    citation = Citation(type="book", title="Test", authors="", year=2023)
    formatter = APAFormatter(citation)
    result = formatter._format_authors([])
    assert result == ""

def test_apa_book_complete_data():
    """Test APA book citation with all fields."""
    citation = Citation(
        type="book",
        title="The Great Book",
        authors=json.dumps(["John Smith", "Alice Doe"]),
        year=2023,
        publisher="Academic Press",
        edition=2
    )
    formatter = APAFormatter(citation)
    result = formatter._format_book(formatter._format_authors(formatter._get_authors_list()))
    expected = "Smith, J., & Doe, A. (2023). <i>The Great Book</i> (2nd ed.). Academic Press."
    assert result == expected

def test_apa_book_minimal_data():
    """Test APA book citation with minimal required fields."""
    citation = Citation(
        type="book",
        title="Simple Book",
        authors=json.dumps(["A Author"]),
        year=2023,
        publisher="Publisher"
    )
    formatter = APAFormatter(citation)
    result = formatter._format_book(formatter._format_authors(formatter._get_authors_list()))
    expected = "Author, A. (2023). <i>Simple Book</i>. Publisher."
    assert result == expected

def test_apa_book_first_edition_ignored():
    """Test that 1st edition is not included in APA citation."""
    citation = Citation(
        type="book",
        title="First Edition Book",
        authors=json.dumps(["A Author"]),
        year=2023,
        publisher="Publisher",
        edition=1
    )
    formatter = APAFormatter(citation)
    result = formatter._format_book(formatter._format_authors(formatter._get_authors_list()))
    expected = "Author, A. (2023). <i>First Edition Book</i>. Publisher."
    assert result == expected

def test_apa_article_complete_data():
    """Test APA article citation with all fields."""
    citation = Citation(
        type="article",
        title="Research Findings",
        authors=json.dumps(["Michael Johnson", "Karen Brown", "Robert Wilson"]),
        year=2022,
        journal="Science Journal",
        volume=45,
        issue="3",
        pages="123-145",
        doi="10.1234/science.2022"
    )
    formatter = APAFormatter(citation)
    result = formatter._format_article(formatter._format_authors(formatter._get_authors_list()))
    expected = "Johnson, M., Brown, K., & Wilson, R. (2022). Research Findings. <i>Science Journal</i>, <i>45</i>(3), 123–145. https://doi.org/10.1234/science.2022"
    assert result == expected

def test_apa_article_without_doi():
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
    formatter = APAFormatter(citation)
    result = formatter._format_article(formatter._format_authors(formatter._get_authors_list()))
    expected = "Author, A. (2023). Article Without DOI. <i>Test Journal</i>, <i>1</i>(2), 10–20."
    assert result == expected

def test_apa_article_without_issue():
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
    formatter = APAFormatter(citation)
    result = formatter._format_article(formatter._format_authors(formatter._get_authors_list()))
    expected = "Author, A. (2023). Article Without Issue. <i>Test Journal</i>, <i>1</i>, 10–20."
    assert result == expected

def test_apa_website_complete_data():
    """Test APA website citation with all fields."""
    citation = Citation(
        type="website",
        title="Online Resource",
        authors=json.dumps(["Web Author"]),
        year=2024,
        publisher="Example Website",
        url="https://example.com/resource"
    )
    formatter = APAFormatter(citation)
    result = formatter._format_website(formatter._format_authors(formatter._get_authors_list()))
    expected = "Author, W. (2024). Online Resource. <i>Example Website</i>. https://example.com/resource"
    assert result == expected

def test_apa_website_minimal_data():
    """Test APA website citation with minimal fields."""
    citation = Citation(
        type="website",
        title="Website Title",
        authors=json.dumps(["Web Author"]),
        year=2024,
        publisher="Sample Site",
        url="https://example.com"
    )
    formatter = APAFormatter(citation)
    result = formatter._format_website(formatter._format_authors(formatter._get_authors_list()))
    expected = "Author, W. (2024). Website Title. <i>Sample Site</i>. https://example.com"
    assert result == expected

def test_apa_report_complete_data():
    """Test APA report citation with all fields."""
    citation = Citation(
        type="report",
        title="Annual Report on Climate Change",
        authors=json.dumps(["Sarah Graduate"]),
        year=2021,
        publisher="Environmental Research Institute",
        url="https://example.org/climate-report-2021"
    )
    formatter = APAFormatter(citation)
    result = formatter._format_report(formatter._format_authors(formatter._get_authors_list()))
    expected = "Graduate, S. (2021). <i>Annual Report on Climate Change</i> [Report]. Environmental Research Institute. https://example.org/climate-report-2021"
    assert result == expected

def test_apa_report_without_url():
    """Test APA report citation without URL."""
    citation = Citation(
        type="report",
        title="Technical Report",
        authors=json.dumps(["M Student"]),
        year=2023,
        publisher="Tech Research Corp"
    )
    formatter = APAFormatter(citation)
    result = formatter._format_report(formatter._format_authors(formatter._get_authors_list()))
    expected = "Student, M. (2023). <i>Technical Report</i> [Report]. Tech Research Corp."
    assert result == expected

def test_apa_citation_missing_fields_handled_gracefully():
    """Test that missing fields are handled gracefully."""
    citation = Citation(
        type="book",
        title="Incomplete Book",
        authors=json.dumps([]),
        year=None,
        publisher=None
    )
    formatter = APAFormatter(citation)
    result = formatter._format_book(formatter._format_authors(formatter._get_authors_list()))
    expected = "(n.d.). <i>Incomplete Book</i>."
    assert result == expected

def test_apa_citation_unsupported_type():
    """Test handling of unsupported citation types."""
    citation = Citation(
        type="unknown_type",
        title="Unknown Type",
        authors=json.dumps(["Author, A."]),
        year=2023
    )
    formatter = APAFormatter(citation)
    
    # APA formatter returns string for unsupported types instead of raising exception
    result = formatter.format_citation()
    expected = "Unsupported citation type: unknown_type"
    assert result == expected

def test_apa_book_no_authors():
    """Test APA book citation with no authors."""
    citation = Citation(
        type="book",
        title="Authorless Book",
        authors=json.dumps([]),
        year=2023,
        publisher="Anonymous Press"
    )
    formatter = APAFormatter(citation)
    result = formatter._format_book(formatter._format_authors(formatter._get_authors_list()))
    expected = "(2023). <i>Authorless Book</i>. Anonymous Press."
    assert result == expected

def test_apa_article_no_volume_or_pages():
    """Test APA article citation without volume or pages."""
    citation = Citation(
        type="article",
        title="Basic Article",
        authors=json.dumps(["A Author"]),
        year=2023,
        journal="Simple Journal"
    )
    formatter = APAFormatter(citation)
    result = formatter._format_article(formatter._format_authors(formatter._get_authors_list()))
    expected = "Author, A. (2023). Basic Article. <i>Simple Journal</i>."
    assert result == expected

def test_apa_website_no_url():
    """Test APA website citation without URL."""
    citation = Citation(
        type="website",
        title="Website Without URL",
        authors=json.dumps(["A Author"]),
        year=2023,
        publisher="Test Site"
    )
    formatter = APAFormatter(citation)
    result = formatter._format_website(formatter._format_authors(formatter._get_authors_list()))
    expected = "Author, A. (2023). Website Without URL. <i>Test Site</i>."
    assert result == expected

def test_apa__normalize_edition_various():
    """Test APA edition normalization."""
    citation = Citation(type="book")
    formatter = APAFormatter(citation)
    
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

def test_apa__get_authors_list_various_formats():
    """Test _get_authors_list method with various input formats."""
    # Valid JSON array
    citation = Citation(type="book", authors=json.dumps(["John Smith", "Jane Doe"]))
    formatter = APAFormatter(citation)
    assert formatter._get_authors_list() == ["John Smith", "Jane Doe"]
    
    # Empty array
    citation.authors = json.dumps([])
    formatter = APAFormatter(citation)
    assert formatter._get_authors_list() == []
    
    # None
    citation.authors = None
    formatter = APAFormatter(citation)
    assert formatter._get_authors_list() == []
    
    # Invalid JSON (fallback to string splitting)
    citation.authors = "John Smith"
    formatter = APAFormatter(citation)
    assert formatter._get_authors_list() == ["John Smith"]


# ========== SPECIFIC MISSING TEST CASES ==========

def test_apa_book_with_advanced_edition_in_real_citation():
    """Test APA book with advanced edition (21st ed.) integrated in real citation."""
    citation = Citation(
        type="book",
        title="Advanced Research Methods",
        authors=json.dumps(["Smith, John A.", "Doe, Jane B."]),
        year=2023,
        publisher="Academic Press",
        edition=21
    )
    formatter = APAFormatter(citation)
    result = formatter.format_citation()
    
    assert "21st ed." in result
    expected = "A., S. J., & B., D. J. (2023). <i>Advanced Research Methods</i> (21st ed.). Academic Press."
    assert result == expected


def test_apa_article_year_none_shows_nd():
    """Test APA article with year=None shows (n.d.)."""
    citation = Citation(
        type="article",
        title="Article Without Year",
        authors=json.dumps(["Author, First"]),
        year=None,
        journal="Test Journal",
        volume="5",
        pages="10-20"
    )
    formatter = APAFormatter(citation)
    result = formatter.format_citation()
    
    assert "(n.d.)" in result
    expected = "First, A. (n.d.). Article Without Year. <i>Test Journal</i>, <i>5</i>, 10–20."
    assert result == expected


def test_apa_article_multiple_page_ranges():
    """Test APA article with multiple page ranges converts hyphens to en-dashes."""
    citation = Citation(
        type="article",
        title="Complex Study",
        authors=json.dumps(["Researcher, A."]),
        year=2023,
        journal="Research Journal",
        volume="10",
        pages="123-125, 200-210"
    )
    formatter = APAFormatter(citation)
    result = formatter.format_citation()
    
    assert "123–125, 200–210" in result
    expected = "A., R. (2023). Complex Study. <i>Research Journal</i>, <i>10</i>, 123–125, 200–210."
    assert result == expected


def test_apa_website_year_none_shows_nd():
    """Test APA website with year=None shows (n.d.)."""
    citation = Citation(
        type="website",
        title="Website Without Year",
        authors=json.dumps(["Web Author"]),
        year=None,
        publisher="Example Site",
        url="https://example.com"
    )
    formatter = APAFormatter(citation)
    result = formatter.format_citation()
    
    assert "(n.d.)" in result
    expected = "Author, W. (n.d.). Website Without Year. <i>Example Site</i>. https://example.com"
    assert result == expected


def test_apa_report_year_none_shows_nd():
    """Test APA report with year=None shows (n.d.)."""
    citation = Citation(
        type="report",
        title="Annual Report",
        authors=json.dumps(["Institution Staff"]),
        year=None,
        publisher="Research Institution"
    )
    formatter = APAFormatter(citation)
    result = formatter.format_citation()
    
    assert "(n.d.)" in result
    expected = "Staff, I. (n.d.). <i>Annual Report</i> [Report]. Research Institution."
    assert result == expected


def test_apa_authors_more_than_20_shows_ellipsis():
    """Test APA with 21+ authors shows first 19 + ... + last author (APA 7 rule)."""
    # Generate 25 authors
    authors_list = [f"Author{i:02d} First{i:02d}" for i in range(1, 26)]
    
    citation = Citation(
        type="book",
        title="Collaborative Research",
        authors=json.dumps(authors_list),
        year=2023,
        publisher="Academic Press"
    )
    formatter = APAFormatter(citation)
    result = formatter.format_citation()
    
    # Should include first 19 authors + ... + last author
    assert "First01, A." in result  # First author (normalized)
    assert "First19, A." in result  # 19th author
    assert "..." in result  # Ellipsis
    assert "First25, A." in result  # Last author (25th)
    
    # Should NOT include author 20-24
    assert "First20, A." not in result
    assert "First21, A." not in result
    assert "First24, A." not in result
    
    # Verify proper formatting
    formatted_authors = formatter._format_authors(authors_list)
    expected_pattern = "First01, A., First02, A., First03, A., First04, A., First05, A., First06, A., First07, A., First08, A., First09, A., First10, A., First11, A., First12, A., First13, A., First14, A., First15, A., First16, A., First17, A., First18, A., First19, A., ..., & First25, A."
    assert formatted_authors == expected_pattern


def test_apa_authors_exactly_20_no_ellipsis():
    """Test APA with exactly 20 authors lists all without ellipsis."""
    # Generate exactly 20 authors
    authors_list = [f"Author{i:02d} First{i:02d}" for i in range(1, 21)]
    
    citation = Citation(
        type="book",
        title="Twenty Authors Book",
        authors=json.dumps(authors_list),
        year=2023,
        publisher="Academic Press"
    )
    formatter = APAFormatter(citation)
    formatted_authors = formatter._format_authors(authors_list)
    
    # Should NOT have ellipsis for exactly 20 authors
    assert "..." not in formatted_authors
    assert "First01, A." in formatted_authors
    assert "First20, A." in formatted_authors
    assert formatted_authors.endswith(", & First20, A.")
