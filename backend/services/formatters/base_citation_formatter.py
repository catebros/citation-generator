# backend/services/formatters/base_citation_formatter.py
import json
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    from models.citation import Citation


class BaseCitationFormatter(ABC):
    """Abstract base class for citation formatters implementing style-specific formatting."""

    def __init__(self, citation: "Citation"):
        """Initialize formatter with citation data."""
        self._citation = citation

    @abstractmethod
    def format_citation(self) -> str:
        """Format citation according to the specific academic style."""
        pass

    @abstractmethod
    def _format_book(self, authors: str) -> str:
        """Format book citation according to specific style."""
        pass

    @abstractmethod
    def _format_article(self, authors: str) -> str:
        """Format article citation according to specific style."""
        pass

    @abstractmethod
    def _format_website(self, authors: str) -> str:
        """Format website citation according to specific style."""
        pass

    @abstractmethod
    def _format_report(self, authors: str) -> str:
        """Format report citation according to specific style."""
        pass

    @abstractmethod
    def _normalize_author_name(self, author: str) -> str:
        """Normalize author name according to specific style format."""
        pass

    @abstractmethod
    def _format_authors(self, authors: List[str]) -> str:
        """Format authors list according to specific style format."""
        pass

    def _get_authors_list(self) -> List[str]:
        """Parse authors from JSON string to Python list."""
        try:
            return json.loads(self._citation.authors) if self._citation.authors else []
        except (json.JSONDecodeError, TypeError):
            return [self._citation.authors] if self._citation.authors else []

    def _clean_authors(self, authors: str) -> str:
        """Remove trailing period from formatted authors string."""
        return authors.rstrip(".")

    def _normalize_edition(self, edition) -> str:
        """Normalize edition number to ordinal format (e.g., 2nd ed., 3rd ed.)."""
        # Validate edition type and convert if necessary
        if edition is None or edition == 1:
            return ""  # Don't show first edition

        # Handle special cases for numbers ending in 11, 12, 13 (always "th")
        if 10 <= edition % 100 <= 13:
            return f"{edition}th ed."

        # Handle based on last digit
        last_digit = edition % 10
        if last_digit == 1:
            return f"{edition}st ed."
        elif last_digit == 2:
            return f"{edition}nd ed."
        elif last_digit == 3:
            return f"{edition}rd ed."
        else:
            return f"{edition}th ed."
