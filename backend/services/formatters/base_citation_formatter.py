# backend/services/formatters/base_citation_formatter.py
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING
import json
from models.citation import Citation

class BaseCitationFormatter(ABC):
    """Abstract base class for citation formatters."""
    
    def __init__(self, citation: 'Citation'):
        """Initialize formatter with citation data."""
        self.citation = citation
    
    @abstractmethod
    def format_citation(self) -> str:
        """Format a citation according to the specific style."""
        pass
    
    @abstractmethod
    def _format_book(self, authors: str) -> str:
        """Format a book citation."""
        pass
    
    @abstractmethod
    def _format_article(self, authors: str) -> str:
        """Format an article citation."""
        pass
    
    @abstractmethod
    def _format_website(self, authors: str) -> str:
        """Format a website citation."""
        pass
    
    @abstractmethod
    def _format_report(self, authors: str) -> str:
        """Format a report citation."""
        pass
    
    @abstractmethod
    def _normalize_author_name(self, author: str) -> str:
        """Normalize author name according to the specific style format."""
        pass
    
    @abstractmethod
    def _format_authors(self, authors: list) -> str:
        """Format authors list according to the specific style format."""
        pass
    
    def _get_authors_list(self) -> list:
        """Parse authors from JSON string to list."""
        try:
            return json.loads(self.citation.authors) if self.citation.authors else []
        except (json.JSONDecodeError, TypeError):
            return [self.citation.authors] if self.citation.authors else []
    
    def _normalize_edition(self, edition) -> str:
        """Normalize edition format.
        Examples: 2 -> '2nd ed.', 3 -> '3rd ed.', 21 -> '21st ed.', 101 -> '101st ed.'
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