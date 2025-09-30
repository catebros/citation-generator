import pytest
import json
from models.citation import Citation
from services.formatters.mla_formatter import MLAFormatter


class TestMLAFormatter:
    """Test suite for MLA citation formatter."""

    def test_mla_book_single_author(self):
        """Test MLA book citation with single author."""
        citation = Citation(
            type="book",
            title="To Kill a Mockingbird",
            authors=json.dumps(["Harper Lee"]),
            year=1960,
            publisher="J.B. Lippincott & Co."
        )
        formatter = MLAFormatter(citation)
        result = formatter.format_book(formatter.format_authors_mla(formatter.get_authors_list()))
        expected = "Lee, Harper. *To Kill a Mockingbird*. J.B. Lippincott & Co., 1960."
        assert result == expected

    def test_mla_book_two_authors(self):
        """Test MLA book citation with two authors."""
        citation = Citation(
            type="book",
            title="The Great Book",
            authors=json.dumps(["John Smith", "Alice Doe"]),
            year=2023,
            publisher="Academic Press"
        )
        formatter = MLAFormatter(citation)
        result = formatter.format_book(formatter.format_authors_mla(formatter.get_authors_list()))
        expected = "Smith, John, and Alice Doe. *The Great Book*. Academic Press, 2023."
        assert result == expected

    def test_mla_book_three_authors(self):
        """Test MLA book citation with three authors."""
        citation = Citation(
            type="book",
            title="Research Methods",
            authors=json.dumps(["John Smith", "Alice Doe", "Bob Johnson"]),
            year=2022,
            publisher="Research Press"
        )
        formatter = MLAFormatter(citation)
        result = formatter.format_book(formatter.format_authors_mla(formatter.get_authors_list()))
        expected = "Smith, John, Alice Doe, and Bob Johnson. *Research Methods*. Research Press, 2022."
        assert result == expected

    def test_mla_book_with_edition(self):
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
        result = formatter.format_book(formatter.format_authors_mla(formatter.get_authors_list()))
        expected = "Developer, Jane. *Programming Fundamentals*. 3rd ed., Tech Books, 2023."
        assert result == expected

    def test_mla_book_first_edition_ignored(self):
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
        result = formatter.format_book(formatter.format_authors_mla(formatter.get_authors_list()))
        expected = "Name, Author. *First Edition Book*. Publisher, 2023."
        assert result == expected

    def test_mla_article_complete_data(self):
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
        result = formatter.format_article(formatter.format_authors_mla(formatter.get_authors_list()))
        expected = 'Smith, Jane, and John Doe. "Climate Change Effects." *Environmental Science Today*, vol. 45, no. 2, 2023, pp. 123–145. https://doi.org/10.1234/est.2023.45.2.123.'
        assert result == expected

    def test_mla_article_without_doi(self):
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
        result = formatter.format_article(formatter.format_authors_mla(formatter.get_authors_list()))
        expected = 'Johnson, Alice. "Research Study." *Science Journal*, vol. 30, 2022, pp. 45–60.'
        assert result == expected

    def test_mla_article_without_issue(self):
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
        result = formatter.format_article(formatter.format_authors_mla(formatter.get_authors_list()))
        expected = 'Writer, Bob. "Simple Study." *Research Today*, vol. 15, 2023, pp. 10–20.'
        assert result == expected

    def test_mla_website_complete_data(self):
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
        result = formatter.format_website(formatter.format_authors_mla(formatter.get_authors_list()))
        expected = 'Team, Environmental. "Understanding Climate Change." *Climate Organization*, 2023, https://example.org/climate-change.'
        assert result == expected

    def test_mla_website_without_author(self):
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
        result = formatter.format_website(formatter.format_authors_mla(formatter.get_authors_list()))
        expected = '"News Article." *News Site*, 2023, https://example.org/news.'
        assert result == expected

    def test_mla_website_without_access_date(self):
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
        result = formatter.format_website(formatter.format_authors_mla(formatter.get_authors_list()))
        expected = 'Author, Web. "Online Resource." *Web Publisher*, 2023, https://example.org/resource.'
        assert result == expected

    def test_mla_report_complete_data(self):
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
        result = formatter.format_report(formatter.format_authors_mla(formatter.get_authors_list()))
        expected = "Graduate, Sarah. *Annual Climate Report*. Environmental Research Institute, 2021. https://example.org/climate-report-2021."
        assert result == expected

    def test_mla_report_without_url(self):
        """Test MLA report citation without URL."""
        citation = Citation(
            type="report",
            title="Technical Report",
            authors=json.dumps(["M Student"]),
            year=2023,
            publisher="Tech Research Corp"
        )
        formatter = MLAFormatter(citation)
        result = formatter.format_report(formatter.format_authors_mla(formatter.get_authors_list()))
        expected = "Student, M. *Technical Report*. Tech Research Corp, 2023."
        assert result == expected

    def test_mla_format_authors_single(self):
        """Test MLA author formatting for single author."""
        citation = Citation(
            type="book",
            authors=json.dumps(["John Smith"])
        )
        formatter = MLAFormatter(citation)
        result = formatter.format_authors_mla(formatter.get_authors_list())
        expected = "Smith, John"
        assert result == expected

    def test_mla_format_authors_two(self):
        """Test MLA author formatting for two authors."""
        citation = Citation(
            type="book",
            authors=json.dumps(["John Smith", "Alice Doe"])
        )
        formatter = MLAFormatter(citation)
        result = formatter.format_authors_mla(formatter.get_authors_list())
        expected = "Smith, John, and Alice Doe"
        assert result == expected

    def test_mla_format_authors_three_or_more(self):
        """Test MLA author formatting for three or more authors."""
        citation = Citation(
            type="book",
            authors=json.dumps(["John Smith", "Alice Doe", "Bob Johnson", "Carol White"])
        )
        formatter = MLAFormatter(citation)
        result = formatter.format_authors_mla(formatter.get_authors_list())
        expected = "Smith, John, Alice Doe, Bob Johnson, and Carol White"
        assert result == expected

    def test_mla_format_authors_empty(self):
        """Test MLA author formatting for empty authors."""
        citation = Citation(
            type="book",
            authors=json.dumps([])
        )
        formatter = MLAFormatter(citation)
        result = formatter.format_authors_mla(formatter.get_authors_list())
        expected = ""
        assert result == expected

    def test_mla_normalize_edition_various(self):
        """Test MLA edition normalization."""
        citation = Citation(type="book")
        formatter = MLAFormatter(citation)
        
        # Test various editions
        assert formatter.normalize_edition(1) == ""  # First edition ignored
        assert formatter.normalize_edition(2) == "2nd ed."
        assert formatter.normalize_edition(3) == "3rd ed."
        assert formatter.normalize_edition(4) == "4th ed."
        assert formatter.normalize_edition(21) == "21st ed."
        assert formatter.normalize_edition(22) == "22nd ed."
        assert formatter.normalize_edition(23) == "23rd ed."
        assert formatter.normalize_edition(24) == "24th ed."

    def test_mla_unsupported_citation_type(self):
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

    def test_mla_missing_required_fields_handled_gracefully(self):
        """Test MLA formatter handles missing fields gracefully."""
        citation = Citation(
            type="book",
            title="",  # Empty title
            authors=json.dumps([]),  # No authors
            year=None,  # No year
            publisher=""  # Empty publisher
        )
        formatter = MLAFormatter(citation)
        result = formatter.format_book(formatter.format_authors_mla(formatter.get_authors_list()))
        
        # Should handle missing fields without crashing
        assert isinstance(result, str)
        assert "n.d." in result  # Should show "no date"
