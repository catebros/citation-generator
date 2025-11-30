# backend/services/formatters/mla_formatter.py
from datetime import datetime
from typing import TYPE_CHECKING, List

from .base_citation_formatter import BaseCitationFormatter
from .formatter_constants import MLA_LOWERCASE_WORDS

if TYPE_CHECKING:
    from models.citation import Citation


class MLAFormatter(BaseCitationFormatter):
    """Format citations according to MLA 9th edition guidelines."""

    def __init__(self, citation: "Citation"):
        """Initialize MLA formatter with citation data."""
        super().__init__(citation)

    def _to_title_case(self, title: str) -> str:
        """Convert title to MLA title case with capitalization rules for major words."""
        if not title:
            return ""

        # Split by colon to handle subtitles
        parts = title.split(":")
        processed_parts = []

        for part in parts:
            words = part.strip().split()
            if not words:
                processed_parts.append("")
                continue

            title_case_words = []

            for i, word in enumerate(words):
                # Remove punctuation for checking, but keep it for the final word
                clean_word = word.strip('.,;:!?"()[]{}').lower()

                # Always capitalize first and last word of each part
                if i == 0 or i == len(words) - 1:
                    title_case_words.append(word.capitalize())
                # Check if word should remain lowercase
                elif clean_word in MLA_LOWERCASE_WORDS:
                    title_case_words.append(word.lower())
                else:
                    title_case_words.append(word.capitalize())

            processed_parts.append(" ".join(title_case_words))

        return ": ".join(processed_parts)

    def format_citation(self) -> str:
        """Route citation to type-specific formatter based on citation type."""
        authors = self._get_authors_list()
        formatted_authors = self._format_authors(authors)

        formatters = {
            "book": self._format_book,
            "article": self._format_article,
            "website": self._format_website,
            "report": self._format_report,
        }

        formatter = formatters.get(self._citation.type)
        if formatter:
            return formatter(formatted_authors)
        return f"Unsupported citation type: {self._citation.type}"

    def _format_authors(self, authors: List[str]) -> str:
        """Format authors per MLA style with first author inverted, et al. for 4+."""
        if not authors:
            return ""

        # First author is always in "Last, First" format
        first_author = self._normalize_author_name(authors[0])

        if len(authors) == 1:
            return first_author
        elif len(authors) == 2:
            # First author: Last, First; Second author: First Last (keep original format)
            second_author = authors[1].strip()
            return f"{first_author}, and {second_author}"
        elif len(authors) == 3:
            # Three authors: First author: Last, First; Others: First Last (keep original format)
            second_author = authors[1].strip()
            third_author = authors[2].strip()
            return f"{first_author}, {second_author}, and {third_author}"
        else:
            # 4+ authors: First author + et al.
            return f"{first_author}, et al."

    def _normalize_author_name(self, author: str) -> str:
        """Convert author name to MLA format (Last, First) for first author only."""
        author = author.strip()
        if not author:
            return ""

        # Format "First Last" to "Last, First"
        parts = author.split()
        if len(parts) >= 2:
            first_names = parts[:-1]
            last_name = parts[-1]
            first_name_str = " ".join(first_names)
            return f"{last_name}, {first_name_str}"

        # Single name, return as is
        return author

    def _format_access_date(self, date_str: str) -> str:
        """Convert YYYY-MM-DD to MLA access date format (Accessed Day Mon. Year)."""
        try:
            dt = datetime.strptime(date_str, "%Y-%m-%d")
            # Format with day without leading zero, abbreviated month with period, year
            day = str(dt.day)  # Remove leading zero
            month_map = {
                1: "Jan.",
                2: "Feb.",
                3: "Mar.",
                4: "Apr.",
                5: "May",
                6: "Jun.",
                7: "Jul.",
                8: "Aug.",
                9: "Sep.",
                10: "Oct.",
                11: "Nov.",
                12: "Dec.",
            }
            month = month_map[dt.month]
            year = str(dt.year)
            return f"Accessed {day} {month} {year}"
        except ValueError:
            # Fallback if date format is not as expected
            return f"Accessed {date_str}"

    def _format_book(self, authors: str) -> str:
        """Generate MLA book citation with italicized title in title case."""
        citation_parts = []

        if authors:
            citation_parts.append(f"{authors}.")

        # Title in italics with Title Case
        if self._citation.title:
            title_case = self._to_title_case(self._citation.title)
            citation_parts.append(f"<i>{title_case}</i>.")

        # Edition (if not first)
        if self._citation.edition and self._citation.edition != 1:
            edition_text = self._normalize_edition(self._citation.edition)
            if edition_text:
                citation_parts.append(f"{edition_text},")

        # Publisher
        if self._citation.publisher:
            citation_parts.append(f"{self._citation.publisher},")

        # Year
        if self._citation.year:
            citation_parts.append(f"{self._citation.year}.")
        else:
            citation_parts.append("n.d.")

        return " ".join(citation_parts)

    def _format_article(self, authors: str) -> str:
        """Generate MLA article citation with quoted title and italicized journal name."""
        citation_parts = []

        if authors:
            citation_parts.append(f"{authors}.")

        # Article title in quotes with Title Case
        if self._citation.title:
            title_case = self._to_title_case(self._citation.title)
            citation_parts.append(f'"{title_case}."')

        # Journal name in italics
        journal_part = []
        if self._citation.journal:
            journal_title_case = self._to_title_case(self._citation.journal)
            journal_part.append(f"<i>{journal_title_case}</i>")

            if self._citation.volume:
                vol_issue = f"vol. {self._citation.volume}"
                if self._citation.issue:
                    vol_issue += f", no. {self._citation.issue}"
                journal_part.append(vol_issue)

            if self._citation.year:
                journal_part.append(str(self._citation.year))
            else:
                journal_part.append("n.d.")

            if self._citation.pages:
                pages_formatted = self._citation.pages.replace("-", "–")
                journal_part.append(f"pp. {pages_formatted}")

        if journal_part:
            citation_parts.append(", ".join(journal_part) + ".")

        # DOI or URL – should always be the last element, NO period at end
        if self._citation.doi:
            citation_parts.append(f"https://doi.org/{self._citation.doi}")
        elif self._citation.url:
            citation_parts.append(f"{self._citation.url}")

        return " ".join(citation_parts)

    def _format_website(self, authors: str) -> str:
        """Generate MLA website citation with quoted title, italicized publisher, and access date."""
        citation_parts = []

        if authors:
            citation_parts.append(f"{authors}.")

        # Title in quotes with Title Case
        if self._citation.title:
            title_case = self._to_title_case(self._citation.title)
            citation_parts.append(f'"{title_case}."')

        # Website name in italics with Title Case
        if self._citation.publisher:
            publisher_title_case = self._to_title_case(self._citation.publisher)
            website_part = f"<i>{publisher_title_case}</i>"
            citation_parts.append(f"{website_part},")

        # With publication date
        if self._citation.year:
            citation_parts.append(f"{self._citation.year},")
            if self._citation.url:
                citation_parts.append(f"{self._citation.url}")
        else:
            # Without publication date -> include access date
            if self._citation.url:
                citation_parts.append(f"{self._citation.url}.")
            if self._citation.access_date:
                formatted_date = self._format_access_date(self._citation.access_date)
                citation_parts.append(f"{formatted_date}.")
            else:
                citation_parts.append("Accessed [Date].")

        return " ".join(citation_parts)

    def _format_report(self, authors: str) -> str:
        """Generate MLA report citation with italicized title and access URL."""
        citation_parts = []

        if authors:
            citation_parts.append(f"{authors}.")

        # Title in italics with Title Case
        if self._citation.title:
            title_case = self._to_title_case(self._citation.title)
            citation_parts.append(f"<i>{title_case}</i>.")

        # Institution/Publisher + Year (grouped to avoid double commas)
        if self._citation.publisher:
            pub_year = self._citation.publisher
            if self._citation.year:
                pub_year += f", {self._citation.year}"
            else:
                pub_year += ", n.d."
            citation_parts.append(f"{pub_year}.")

        # URL without period at end
        if self._citation.url:
            citation_parts.append(f"{self._citation.url}")

        return " ".join(citation_parts)
