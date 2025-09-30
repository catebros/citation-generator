from abc import ABC, abstractmethod
from typing import TYPE_CHECKING
import json

if TYPE_CHECKING:
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
    def format_book(self, authors: str) -> str:
        """Format a book citation."""
        pass
    
    @abstractmethod
    def format_article(self, authors: str) -> str:
        """Format an article citation."""
        pass
    
    @abstractmethod
    def format_website(self, authors: str) -> str:
        """Format a website citation."""
        pass
    
    @abstractmethod
    def format_report(self, authors: str) -> str:
        """Format a report citation."""
        pass
    
    def get_authors_list(self) -> list:
        """Parse authors from JSON string to list."""
        try:
            return json.loads(self.citation.authors) if self.citation.authors else []
        except (json.JSONDecodeError, TypeError):
            return [self.citation.authors] if self.citation.authors else []
    
    def normalize_edition(self, edition: int) -> str:
        """Normalize edition format.
        Examples: 2 -> '2nd ed.', 3 -> '3rd ed.'
        """
        if not edition or edition == 1:
            return ""  # Don't show first edition
        
        if edition == 2:
            return "2nd ed."
        elif edition == 3:
            return "3rd ed."
        elif edition in [21, 31, 41, 51, 61, 71, 81, 91]:
            return f"{edition}st ed."
        elif edition in [22, 32, 42, 52, 62, 72, 82, 92]:
            return f"{edition}nd ed."
        elif edition in [23, 33, 43, 53, 63, 73, 83, 93]:
            return f"{edition}rd ed."
        else:
            return f"{edition}th ed."