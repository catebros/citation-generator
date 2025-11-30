# backend/tests/test_mla_formatter.py
import json

import pytest
from models.citation import Citation
from services.formatters.mla_formatter import MLAFormatter

def test_mla_book_single_author():
    """Test MLA book citation with single author."""
    citation = Citation(
        type="book",
        title="To Kill a Mockingbird",
        authors=json.dumps(["Harper Lee"]),
        year=1960,
        publisher="J.B. Lippincott & Co.",
    )
    formatter = MLAFormatter(citation)
    result = formatter._format_book(
        formatter._format_authors(formatter._get_authors_list())
    )
    expected = "Lee, Harper. <i>To Kill a Mockingbird</i>. J.B. Lippincott & Co., 1960."
    assert result == expected


def test_mla_book_two_authors():
    """Test MLA book citation with two authors."""
    citation = Citation(
        type="book",
        title="The Great Book",
        authors=json.dumps(["John Smith", "Alice Doe"]),
        year=2023,
        publisher="Academic Press",
    )
    formatter = MLAFormatter(citation)
    result = formatter._format_book(
        formatter._format_authors(formatter._get_authors_list())
    )
    expected = (
        "Smith, John, and Alice Doe. <i>The Great Book</i>. Academic Press, 2023."
    )
    assert result == expected


def test_mla_book_three_authors():
    """Test MLA book citation with three authors."""
    citation = Citation(
        type="book",
        title="Research Methods",
        authors=json.dumps(["John Smith", "Alice Doe", "Bob Johnson"]),
        year=2022,
        publisher="Research Press",
    )
    formatter = MLAFormatter(citation)
    result = formatter._format_book(
        formatter._format_authors(formatter._get_authors_list())
    )
    expected = "Smith, John, Alice Doe, and Bob Johnson. <i>Research Methods</i>. Research Press, 2022."
    assert result == expected


def test_mla_book_with_edition():
    """Test MLA book citation with edition."""
    citation = Citation(
        type="book",
        title="Programming Fundamentals",
        authors=json.dumps(["Jane Developer"]),
        year=2023,
        publisher="Tech Books",
        edition=3,
    )
    formatter = MLAFormatter(citation)
    result = formatter._format_book(
        formatter._format_authors(formatter._get_authors_list())
    )
    expected = (
        "Developer, Jane. <i>Programming Fundamentals</i>. 3rd ed., Tech Books, 2023."
    )
    assert result == expected


def test_mla_book_first_edition_ignored():
    """Test MLA book citation ignores first edition."""
    citation = Citation(
        type="book",
        title="First Edition Book",
        authors=json.dumps(["Author Name"]),
        year=2023,
        publisher="Publisher",
        edition=1,
    )
    formatter = MLAFormatter(citation)
    result = formatter._format_book(
        formatter._format_authors(formatter._get_authors_list())
    )
    expected = "Name, Author. <i>First Edition Book</i>. Publisher, 2023."
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
        doi="10.1234/est.2023.45.2.123",
    )
    formatter = MLAFormatter(citation)
    result = formatter._format_article(
        formatter._format_authors(formatter._get_authors_list())
    )
    expected = (
        'Smith, Jane, and John Doe. "Climate Change Effects." '
        "<i>Environmental Science Today</i>, vol. 45, no. 2, 2023, pp. 123–145. "
        "https://doi.org/10.1234/est.2023.45.2.123"
    )
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
        pages="45-60",
    )
    formatter = MLAFormatter(citation)
    result = formatter._format_article(
        formatter._format_authors(formatter._get_authors_list())
    )
    expected = 'Johnson, Alice. "Research Study." <i>Science Journal</i>, vol. 30, 2022, pp. 45–60.'
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
        pages="10-20",
    )
    formatter = MLAFormatter(citation)
    result = formatter._format_article(
        formatter._format_authors(formatter._get_authors_list())
    )
    expected = (
        'Writer, Bob. "Simple Study." <i>Research Today</i>, vol. 15, 2023, pp. 10–20.'
    )
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
        access_date="15 Mar. 2023",
    )
    formatter = MLAFormatter(citation)
    result = formatter._format_website(
        formatter._format_authors(formatter._get_authors_list())
    )
    expected = (
        'Team, Environmental. "Understanding Climate Change." '
        "<i>Climate Organization</i>, 2023, "
        "https://example.org/climate-change"
    )
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
        access_date="20 Jan. 2023",
    )
    formatter = MLAFormatter(citation)
    result = formatter._format_website(
        formatter._format_authors(formatter._get_authors_list())
    )
    expected = '"News Article." <i>News Site</i>, 2023, https://example.org/news'
    assert result == expected


def test_mla_website_without_access_date():
    """Test MLA website citation without access date."""
    citation = Citation(
        type="website",
        title="Online Resource",
        authors=json.dumps(["Web Author"]),
        year=2023,
        publisher="Web Publisher",
        url="https://example.org/resource",
    )
    formatter = MLAFormatter(citation)
    result = formatter._format_website(
        formatter._format_authors(formatter._get_authors_list())
    )
    expected = 'Author, Web. "Online Resource." <i>Web Publisher</i>, 2023, https://example.org/resource'
    assert result == expected


def test_mla_report_complete_data():
    """Test MLA report citation with complete data."""
    citation = Citation(
        type="report",
        title="Annual Climate Report",
        authors=json.dumps(["Sarah Graduate"]),
        year=2021,
        publisher="Environmental Research Institute",
        url="https://example.org/climate-report-2021",
    )
    formatter = MLAFormatter(citation)
    result = formatter._format_report(
        formatter._format_authors(formatter._get_authors_list())
    )
    expected = (
        "Graduate, Sarah. <i>Annual Climate Report</i>. "
        "Environmental Research Institute, 2021. "
        "https://example.org/climate-report-2021"
    )
    assert result == expected


def test_mla_report_without_url():
    """Test MLA report citation without URL."""
    citation = Citation(
        type="report",
        title="Technical Report",
        authors=json.dumps(["M Student"]),
        year=2023,
        publisher="Tech Research Corp",
    )
    formatter = MLAFormatter(citation)
    result = formatter._format_report(
        formatter._format_authors(formatter._get_authors_list())
    )
    expected = "Student, M. <i>Technical Report</i>. Tech Research Corp, 2023."
    assert result == expected


def test_mla_format_authors_single():
    """Test MLA author formatting for single author."""
    citation = Citation(type="book", authors=json.dumps(["John Smith"]))
    formatter = MLAFormatter(citation)
    result = formatter._format_authors(formatter._get_authors_list())
    expected = "Smith, John"
    assert result == expected


def test_mla_format_authors_two():
    """Test MLA author formatting for two authors."""
    citation = Citation(type="book", authors=json.dumps(["John Smith", "Alice Doe"]))
    formatter = MLAFormatter(citation)
    result = formatter._format_authors(formatter._get_authors_list())
    expected = "Smith, John, and Alice Doe"
    assert result == expected


def test_mla_format_authors_three_or_more():
    """Test MLA author formatting for three or more authors."""
    citation = Citation(
        type="book",
        authors=json.dumps(["John Smith", "Alice Doe", "Bob Johnson", "Carol White"]),
    )
    formatter = MLAFormatter(citation)
    result = formatter._format_authors(formatter._get_authors_list())
    # With 4 authors, MLA now uses et al.
    expected = "Smith, John, et al."
    assert result == expected


def test_mla_format_authors_empty():
    """Test MLA author formatting for empty authors."""
    citation = Citation(type="book", authors=json.dumps([]))
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
        type="unsupported", title="Unknown Type", authors=json.dumps(["Author Name"])
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
        publisher="",  # Empty publisher
    )
    formatter = MLAFormatter(citation)
    result = formatter._format_book(
        formatter._format_authors(formatter._get_authors_list())
    )

    # Should handle missing fields without crashing
    assert isinstance(result, str)
    assert "n.d." in result  # Should show "no date"

def test_mla_book_with_advanced_edition_in_real_citation():
    """Test MLA book with advanced edition (22nd ed.) integrated in real citation."""
    citation = Citation(
        type="book",
        title="Modern Literary Theory",
        authors=json.dumps(["Smith, John", "Johnson, Robert"]),
        year=2023,
        publisher="University Press",
        edition=22,
    )
    formatter = MLAFormatter(citation)
    result = formatter.format_citation()

    assert "22nd ed." in result
    expected = "John, Smith,, and Johnson, Robert. <i>Modern Literary Theory</i>. 22nd ed., University Press, 2023."
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
        pages="45-60",
    )
    formatter = MLAFormatter(citation)
    result = formatter.format_citation()

    assert "n.d." in result
    expected = 'John, Smith,. "Undated Research." <i>Academic Journal</i>, vol. 15, n.d., pp. 45–60.'
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
        access_date="2025-10-02",
    )
    formatter = MLAFormatter(citation)
    result = formatter.format_citation()

    assert "Accessed 2 Oct. 2025" in result
    expected = (
        'Author, Web,. "Online Resource." <i>Example Website</i>, '
        "https://example.com/resource. Accessed 2 Oct. 2025."
    )
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
        access_date="not-a-date",
    )
    formatter = MLAFormatter(citation)
    result = formatter.format_citation()

    assert "Accessed not-a-date" in result
    expected = 'Author, Digital,. "Another Resource." <i>Test Site</i>, https://test.com. Accessed not-a-date.'
    assert result == expected


def test_mla_report_year_none_shows_nd():
    """Test MLA report with year=None shows n.d."""
    citation = Citation(
        type="report",
        title="Technical Report",
        authors=json.dumps(["Institute, Research"]),
        year=None,
        publisher="Government Agency",
    )
    formatter = MLAFormatter(citation)
    result = formatter.format_citation()

    assert "n.d." in result
    expected = "Research, Institute,. <i>Technical Report</i>. Government Agency, n.d.."
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
        publisher="Academic Press",
    )
    formatter = MLAFormatter(citation)
    formatted_authors = formatter._format_authors(authors_list)

    # Should show first author + et al.
    assert formatted_authors == "John, Smith, et al."

    # Test with 10 authors
    many_authors = [f"Author{i} First{i}" for i in range(1, 11)]
    formatted_many = formatter._format_authors(many_authors)
    assert formatted_many == "First1, Author1, et al."


def test_mla_title_case_conversion():
    """Test MLA Title Case conversion with various scenarios."""
    citation = Citation(type="book")
    formatter = MLAFormatter(citation)

    # Test basic title case
    assert formatter._to_title_case("the great gatsby") == "The Great Gatsby"
    assert formatter._to_title_case("to kill a mockingbird") == "To Kill a Mockingbird"

    # Test articles and prepositions (should be lowercase unless first/last)
    assert formatter._to_title_case("a tale of two cities") == "A Tale of Two Cities"
    assert formatter._to_title_case("the lord of the rings") == "The Lord of the Rings"
    assert (
        formatter._to_title_case("much ado about nothing") == "Much Ado About Nothing"
    )

    # Test first and last word always capitalized
    assert formatter._to_title_case("gone with the wind") == "Gone with the Wind"

    # Test conjunctions
    assert formatter._to_title_case("pride and prejudice") == "Pride and Prejudice"
    assert formatter._to_title_case("romeo and juliet") == "Romeo and Juliet"

    # Test empty/None
    assert formatter._to_title_case("") == ""
    assert formatter._to_title_case(None) == ""


def test_mla_book_with_title_case_complex():
    """Test MLA book citation with complex title requiring Title Case."""
    citation = Citation(
        type="book",
        title="the art of computer programming: a comprehensive introduction",
        authors=json.dumps(["Donald Knuth"]),
        year=1968,
        publisher="Addison-Wesley",
    )
    formatter = MLAFormatter(citation)
    result = formatter._format_book(
        formatter._format_authors(formatter._get_authors_list())
    )
    expected = (
        "Knuth, Donald. <i>The Art of Computer Programming: "
        "A Comprehensive Introduction</i>. Addison-Wesley, 1968."
    )
    assert result == expected


def test_mla_article_with_title_case_complex():
    """Test MLA article citation with complex titles requiring Title Case."""
    citation = Citation(
        type="article",
        title="machine learning in the age of artificial intelligence",
        authors=json.dumps(["Jane Smith"]),
        year=2023,
        journal="journal of computer science and technology",
        volume=45,
        issue="2",
        pages="123-145",
    )
    formatter = MLAFormatter(citation)
    result = formatter._format_article(
        formatter._format_authors(formatter._get_authors_list())
    )
    expected = (
        'Smith, Jane. "Machine Learning in the Age of Artificial Intelligence." '
        "<i>Journal of Computer Science and Technology</i>, "
        "vol. 45, no. 2, 2023, pp. 123–145."
    )
    assert result == expected


def test_mla_authors_exactly_three_lists_all():
    """Test MLA with exactly 3 authors lists all authors without et al."""
    authors_list = ["Smith John", "Doe Jane", "Brown Bob"]

    citation = Citation(
        type="book",
        title="Three Authors Book",
        authors=json.dumps(authors_list),
        year=2023,
        publisher="Academic Press",
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

def test_mla_format_access_date_valid_format():
    """Test MLA _format_access_date with valid YYYY-MM-DD format."""
    citation = Citation(type="website")
    formatter = MLAFormatter(citation)

    # Test various valid dates - includes "Accessed" prefix
    assert formatter._format_access_date("2025-01-15") == "Accessed 15 Jan. 2025"
    assert formatter._format_access_date("2023-03-05") == "Accessed 5 Mar. 2023"
    assert formatter._format_access_date("2024-12-31") == "Accessed 31 Dec. 2024"
    assert (
        formatter._format_access_date("2022-07-04") == "Accessed 4 Jul. 2022"
    )  # July is abbreviated


def test_mla_format_access_date_single_digit_day():
    """Test MLA _format_access_date with single-digit days (no leading zero)."""
    citation = Citation(type="website")
    formatter = MLAFormatter(citation)

    # Includes "Accessed" prefix
    assert formatter._format_access_date("2025-10-01") == "Accessed 1 Oct. 2025"
    assert formatter._format_access_date("2025-10-09") == "Accessed 9 Oct. 2025"


def test_mla_format_access_date_all_months():
    """Test MLA _format_access_date with all months."""
    citation = Citation(type="website")
    formatter = MLAFormatter(citation)

    # All include "Accessed" prefix
    assert formatter._format_access_date("2025-01-15") == "Accessed 15 Jan. 2025"
    assert formatter._format_access_date("2025-02-15") == "Accessed 15 Feb. 2025"
    assert formatter._format_access_date("2025-03-15") == "Accessed 15 Mar. 2025"
    assert formatter._format_access_date("2025-04-15") == "Accessed 15 Apr. 2025"
    assert (
        formatter._format_access_date("2025-05-15") == "Accessed 15 May 2025"
    )  # May has no period
    assert (
        formatter._format_access_date("2025-06-15") == "Accessed 15 Jun. 2025"
    )  # June abbreviated
    assert (
        formatter._format_access_date("2025-07-15") == "Accessed 15 Jul. 2025"
    )  # July abbreviated
    assert formatter._format_access_date("2025-08-15") == "Accessed 15 Aug. 2025"
    assert formatter._format_access_date("2025-09-15") == "Accessed 15 Sep. 2025"
    assert formatter._format_access_date("2025-10-15") == "Accessed 15 Oct. 2025"
    assert formatter._format_access_date("2025-11-15") == "Accessed 15 Nov. 2025"
    assert formatter._format_access_date("2025-12-15") == "Accessed 15 Dec. 2025"


def test_mla_format_access_date_invalid_format_returns_as_is():
    """Test MLA _format_access_date with invalid format returns with Accessed prefix."""
    citation = Citation(type="website")
    formatter = MLAFormatter(citation)

    # Invalid formats get "Accessed" prefix added
    assert formatter._format_access_date("01-15-2025") == "Accessed 01-15-2025"
    assert formatter._format_access_date("not-a-date") == "Accessed not-a-date"
    assert formatter._format_access_date("2025/10/15") == "Accessed 2025/10/15"
    assert formatter._format_access_date("") == "Accessed "


def test_mla_format_access_date_none_raises_error():
    """Test MLA _format_access_date with None raises TypeError."""
    citation = Citation(type="website")
    formatter = MLAFormatter(citation)

    # None is not a valid input - method expects string, will raise TypeError
    with pytest.raises(TypeError):
        formatter._format_access_date(None)


def test_mla_normalize_author_name_two_part():
    """Test MLA _normalize_author_name with two-part names."""
    citation = Citation(type="book")
    formatter = MLAFormatter(citation)

    assert formatter._normalize_author_name("John Smith") == "Smith, John"
    assert formatter._normalize_author_name("Alice Johnson") == "Johnson, Alice"
    assert formatter._normalize_author_name("Mary Williams") == "Williams, Mary"


def test_mla_normalize_author_name_three_part():
    """Test MLA _normalize_author_name with three-part names (middle names)."""
    citation = Citation(type="book")
    formatter = MLAFormatter(citation)

    # All first/middle names stay after comma in MLA
    assert formatter._normalize_author_name("John Paul Jones") == "Jones, John Paul"
    assert formatter._normalize_author_name("Mary Jane Watson") == "Watson, Mary Jane"
    assert (
        formatter._normalize_author_name("Michael Thomas Anderson")
        == "Anderson, Michael Thomas"
    )


def test_mla_normalize_author_name_four_part():
    """Test MLA _normalize_author_name with four-part names (multiple middle names)."""
    citation = Citation(type="book")
    formatter = MLAFormatter(citation)

    assert (
        formatter._normalize_author_name("John Paul George Smith")
        == "Smith, John Paul George"
    )
    assert formatter._normalize_author_name("A B C Defgh") == "Defgh, A B C"


def test_mla_normalize_author_name_single_name():
    """Test MLA _normalize_author_name with single names."""
    citation = Citation(type="book")
    formatter = MLAFormatter(citation)

    # Single names returned as-is (no inversion)
    assert formatter._normalize_author_name("Madonna") == "Madonna"
    assert formatter._normalize_author_name("Plato") == "Plato"
    assert formatter._normalize_author_name("Shakespeare") == "Shakespeare"


def test_mla_normalize_author_name_with_spaces():
    """Test MLA _normalize_author_name handles extra spaces."""
    citation = Citation(type="book")
    formatter = MLAFormatter(citation)

    assert formatter._normalize_author_name("  John   Smith  ") == "Smith, John"
    assert formatter._normalize_author_name("John  Paul  Jones") == "Jones, John Paul"


def test_mla_normalize_author_name_empty():
    """Test MLA _normalize_author_name with empty string."""
    citation = Citation(type="book")
    formatter = MLAFormatter(citation)

    assert formatter._normalize_author_name("") == ""
    assert formatter._normalize_author_name("   ") == ""


def test_mla_normalize_author_name_preserves_case():
    """Test MLA _normalize_author_name preserves original case."""
    citation = Citation(type="book")
    formatter = MLAFormatter(citation)

    # MLA preserves case as written
    assert formatter._normalize_author_name("john smith") == "smith, john"
    assert formatter._normalize_author_name("ALICE JOHNSON") == "JOHNSON, ALICE"
    assert formatter._normalize_author_name("Mary Jane") == "Jane, Mary"


def test_mla_normalize_author_name_hyphenated():
    """Test MLA _normalize_author_name with hyphenated last names."""
    citation = Citation(type="book")
    formatter = MLAFormatter(citation)

    # Hyphenated last name is treated as single unit
    assert formatter._normalize_author_name("Jean-Paul Sartre") == "Sartre, Jean-Paul"
    assert formatter._normalize_author_name("Mary Smith-Jones") == "Smith-Jones, Mary"
