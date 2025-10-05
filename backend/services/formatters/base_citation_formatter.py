# backend/services/formatters/base_citation_formatter.py
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, List
import json
from models.citation import Citation

class BaseCitationFormatter(ABC):
    """
    Abstract base class for citation formatters.

    This class defines the common interface and shared functionality for all
    citation formatting styles (APA, MLA, etc.). It provides abstract methods
    that must be implemented by subclasses for style-specific formatting, as well
    as concrete utility methods for common operations like parsing authors and
    normalizing editions.

    Attributes:
        _citation (Citation): The citation object to be formatted
    """

    def __init__(self, citation: 'Citation'):
        """
        Initialize formatter with citation data.

        Args:
            citation (Citation): The citation object containing all citation fields
        """
        self._citation = citation

    @abstractmethod
    def format_citation(self) -> str:
        """
        Format a citation according to the specific academic style.

        Returns:
            str: Formatted citation string

        Note:
            Must be implemented by subclasses for each specific citation style
        """
        pass

    @abstractmethod
    def _format_book(self, authors: str) -> str:
        """
        Format a book citation according to the specific style.

        Args:
            authors (str): Formatted authors string

        Returns:
            str: Formatted book citation

        Note:
            Must be implemented by subclasses for each specific citation style
        """
        pass

    @abstractmethod
    def _format_article(self, authors: str) -> str:
        """
        Format an article citation according to the specific style.

        Args:
            authors (str): Formatted authors string

        Returns:
            str: Formatted article citation

        Note:
            Must be implemented by subclasses for each specific citation style
        """
        pass

    @abstractmethod
    def _format_website(self, authors: str) -> str:
        """
        Format a website citation according to the specific style.

        Args:
            authors (str): Formatted authors string

        Returns:
            str: Formatted website citation

        Note:
            Must be implemented by subclasses for each specific citation style
        """
        pass

    @abstractmethod
    def _format_report(self, authors: str) -> str:
        """
        Format a report citation according to the specific style.

        Args:
            authors (str): Formatted authors string

        Returns:
            str: Formatted report citation

        Note:
            Must be implemented by subclasses for each specific citation style
        """
        pass

    @abstractmethod
    def _normalize_author_name(self, author: str) -> str:
        """
        Normalize author name according to the specific style format.

        Args:
            author (str): Author name in original format

        Returns:
            str: Normalized author name

        Note:
            Must be implemented by subclasses (e.g., "Smith, J." for APA, "Smith, John" for MLA)
        """
        pass

    @abstractmethod
    def _format_authors(self, authors: List[str]) -> str:
        """
        Format authors list according to the specific style format.

        Args:
            authors (list): List of author names

        Returns:
            str: Formatted authors string

        Note:
            Must be implemented by subclasses for style-specific author formatting rules
        """
        pass

    def _get_authors_list(self) -> List[str]:
        """
        Parse authors from JSON string stored in database to Python list.

        This helper method safely extracts the authors list from the citation
        object, handling both JSON-encoded strings and already-parsed lists.

        Returns:
            list: List of author name strings, or empty list if no authors

        Note:
            - Authors are stored as JSON strings in the database
            - Handles JSON decode errors gracefully
            - Returns empty list if authors field is None or empty
        """
        try:
            return json.loads(self._citation.authors) if self._citation.authors else []
        except (json.JSONDecodeError, TypeError):
            return [self._citation.authors] if self._citation.authors else []

    def _normalize_edition(self, edition) -> str:
        """
        Normalize edition number to standardized text format with ordinal suffix.

        Converts integer edition numbers to proper ordinal format following
        English grammar rules for ordinal suffixes.

        Args:
            edition (int): Edition number

        Returns:
            str: Formatted edition string (e.g., "2nd ed.", "3rd ed.", "21st ed.")
                 Empty string if edition is None or 1 (first editions are not shown)

        Examples:
            2 -> "2nd ed."
            3 -> "3rd ed."
            11 -> "11th ed."
            21 -> "21st ed."
            101 -> "101st ed."

        Note:
            - Returns empty string for None or 1 (first edition not displayed)
            - Special handling for 11, 12, 13 which always use "th"
            - Uses proper ordinal suffixes (st, nd, rd, th) based on last digit
        """
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