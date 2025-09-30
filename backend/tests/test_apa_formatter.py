import pytest
import json
from models.citation import Citation
from services.formatters.apa_formatter import APAFormatter


class TestAPAFormatter:
    """Test suite for APA citation formatter."""

    def test_apa_format_authors_single_author(self):
        """Test APA formatting for single author."""
        citation = Citation(type="book", title="Test", authors="", year=2023)
        formatter = APAFormatter(citation)
        result = formatter.format_authors_apa(["John Smith"])
        assert result == "Smith, J."

    def test_apa_format_authors_two_authors(self):
        """Test APA formatting for two authors."""
        citation = Citation(type="book", title="Test", authors="", year=2023)
        formatter = APAFormatter(citation)
        result = formatter.format_authors_apa(["John Smith", "Jane Doe"])
        assert result == "Smith, J., & Doe, J."

    def test_apa_format_authors_three_or_more_authors(self):
        """Test APA formatting for three or more authors."""
        citation = Citation(type="book", title="Test", authors="", year=2023)
        formatter = APAFormatter(citation)
        result = formatter.format_authors_apa(["John Smith", "Jane Doe", "Bob Brown"])
        assert result == "Smith, J., Doe, J., & Brown, B."

    def test_apa_format_authors_empty_list(self):
        """Test APA formatting for empty authors list."""
        citation = Citation(type="book", title="Test", authors="", year=2023)
        formatter = APAFormatter(citation)
        result = formatter.format_authors_apa([])
        assert result == ""

    def test_apa_book_complete_data(self):
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
        result = formatter.format_book(formatter.format_authors_apa(formatter.get_authors_list()))
        expected = "Smith, J., & Doe, A. (2023). *The Great Book* (2nd ed.). Academic Press."
        assert result == expected

    def test_apa_book_minimal_data(self):
        """Test APA book citation with minimal required fields."""
        citation = Citation(
            type="book",
            title="Simple Book",
            authors=json.dumps(["A Author"]),
            year=2023,
            publisher="Publisher"
        )
        formatter = APAFormatter(citation)
        result = formatter.format_book(formatter.format_authors_apa(formatter.get_authors_list()))
        expected = "Author, A. (2023). *Simple Book*. Publisher."
        assert result == expected

    def test_apa_book_first_edition_ignored(self):
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
        result = formatter.format_book(formatter.format_authors_apa(formatter.get_authors_list()))
        expected = "Author, A. (2023). *First Edition Book*. Publisher."
        assert result == expected

    def test_apa_article_complete_data(self):
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
        result = formatter.format_article(formatter.format_authors_apa(formatter.get_authors_list()))
        expected = "Johnson, M., Brown, K., & Wilson, R. (2022). Research Findings. *Science Journal*, 45(3), 123–145. https://doi.org/10.1234/science.2022"
        assert result == expected

    def test_apa_article_without_doi(self):
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
        result = formatter.format_article(formatter.format_authors_apa(formatter.get_authors_list()))
        expected = "Author, A. (2023). Article Without DOI. *Test Journal*, 1(2), 10–20."
        assert result == expected

    def test_apa_article_without_issue(self):
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
        result = formatter.format_article(formatter.format_authors_apa(formatter.get_authors_list()))
        expected = "Author, A. (2023). Article Without Issue. *Test Journal*, 1, 10–20."
        assert result == expected

    def test_apa_website_complete_data(self):
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
        result = formatter.format_website(formatter.format_authors_apa(formatter.get_authors_list()))
        expected = "Author, W. (2024). Online Resource. *Example Website*. https://example.com/resource"
        assert result == expected

    def test_apa_website_minimal_data(self):
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
        result = formatter.format_website(formatter.format_authors_apa(formatter.get_authors_list()))
        expected = "Author, W. (2024). Website Title. *Sample Site*. https://example.com"
        assert result == expected

    def test_apa_report_complete_data(self):
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
        result = formatter.format_report(formatter.format_authors_apa(formatter.get_authors_list()))
        expected = "Graduate, S. (2021). *Annual Report on Climate Change* (report). Environmental Research Institute. https://example.org/climate-report-2021"
        assert result == expected

    def test_apa_report_without_url(self):
        """Test APA report citation without URL."""
        citation = Citation(
            type="report",
            title="Technical Report",
            authors=json.dumps(["M Student"]),
            year=2023,
            publisher="Tech Research Corp"
        )
        formatter = APAFormatter(citation)
        result = formatter.format_report(formatter.format_authors_apa(formatter.get_authors_list()))
        expected = "Student, M. (2023). *Technical Report* (report). Tech Research Corp."
        assert result == expected

    def test_apa_citation_missing_fields_handled_gracefully(self):
        """Test that missing fields are handled gracefully."""
        citation = Citation(
            type="book",
            title="Incomplete Book",
            authors=json.dumps([]),
            year=None,
            publisher=None
        )
        formatter = APAFormatter(citation)
        result = formatter.format_book(formatter.format_authors_apa(formatter.get_authors_list()))
        expected = "(n.d.). *Incomplete Book*."
        assert result == expected

    def test_apa_citation_unsupported_type(self):
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

    def test_apa_book_no_authors(self):
        """Test APA book citation with no authors."""
        citation = Citation(
            type="book",
            title="Authorless Book",
            authors=json.dumps([]),
            year=2023,
            publisher="Anonymous Press"
        )
        formatter = APAFormatter(citation)
        result = formatter.format_book(formatter.format_authors_apa(formatter.get_authors_list()))
        expected = "(2023). *Authorless Book*. Anonymous Press."
        assert result == expected

    def test_apa_article_no_volume_or_pages(self):
        """Test APA article citation without volume or pages."""
        citation = Citation(
            type="article",
            title="Basic Article",
            authors=json.dumps(["A Author"]),
            year=2023,
            journal="Simple Journal"
        )
        formatter = APAFormatter(citation)
        result = formatter.format_article(formatter.format_authors_apa(formatter.get_authors_list()))
        expected = "Author, A. (2023). Basic Article. *Simple Journal*."
        assert result == expected

    def test_apa_website_no_url(self):
        """Test APA website citation without URL."""
        citation = Citation(
            type="website",
            title="Website Without URL",
            authors=json.dumps(["A Author"]),
            year=2023,
            publisher="Test Site"
        )
        formatter = APAFormatter(citation)
        result = formatter.format_website(formatter.format_authors_apa(formatter.get_authors_list()))
        expected = "Author, A. (2023). Website Without URL. *Test Site*."
        assert result == expected

    def test_apa_normalize_edition_various(self):
        """Test APA edition normalization."""
        citation = Citation(type="book")
        formatter = APAFormatter(citation)
        
        # Test various editions
        assert formatter.normalize_edition(1) == ""  # First edition ignored
        assert formatter.normalize_edition(2) == "2nd ed."
        assert formatter.normalize_edition(3) == "3rd ed."
        assert formatter.normalize_edition(4) == "4th ed."
        assert formatter.normalize_edition(21) == "21st ed."
        assert formatter.normalize_edition(22) == "22nd ed."
        assert formatter.normalize_edition(23) == "23rd ed."
        assert formatter.normalize_edition(24) == "24th ed."

    def test_apa_get_authors_list_various_formats(self):
        """Test get_authors_list method with various input formats."""
        # Valid JSON array
        citation = Citation(type="book", authors=json.dumps(["John Smith", "Jane Doe"]))
        formatter = APAFormatter(citation)
        assert formatter.get_authors_list() == ["John Smith", "Jane Doe"]
        
        # Empty array
        citation.authors = json.dumps([])
        formatter = APAFormatter(citation)
        assert formatter.get_authors_list() == []
        
        # None
        citation.authors = None
        formatter = APAFormatter(citation)
        assert formatter.get_authors_list() == []
        
        # Invalid JSON (fallback to string splitting)
        citation.authors = "John Smith"
        formatter = APAFormatter(citation)
        assert formatter.get_authors_list() == ["John Smith"]