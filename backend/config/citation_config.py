# backend/config/citation_config.py
from typing import Dict, List
import copy


class CitationFieldsConfig:
    """
    Singleton class for managing citation configuration.
    This ensures only one instance of the configuration exists throughout the application.
    """
    _instance = None
    _initialized = False

    def __new__(cls) -> 'CitationFieldsConfig':
        """
        Create a new instance only if one doesn't exist.

        Returns:
            CitationFieldsConfig: The singleton instance of the configuration class
        """
        if cls._instance is None:
            cls._instance = super(CitationFieldsConfig, cls).__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        """
        Initialize the configuration data only once.

        Defines the required fields for each supported citation type:
        - book: Requires type, title, authors, year, publisher, place, edition
        - article: Requires type, title, authors, year, journal, volume, issue, pages, doi
        - website: Requires type, title, authors, year, publisher, url, access_date
        - report: Requires type, title, authors, year, publisher, url, place
        """
        if not self._initialized:
            self._required_for_citation_types = {
                "book": ["type", "title", "authors", "year", "publisher", "place", "edition"],
                "article": ["type", "title", "authors", "year", "journal", "volume", "issue", "pages", "doi"],
                "website": ["type", "title", "authors", "year", "publisher", "url", "access_date"],
                "report": ["type", "title", "authors", "year", "publisher", "url", "place"]
            }
            
            CitationFieldsConfig._initialized = True

    def get_required_for_citation_types(self) -> Dict[str, List[str]]:
        """
        Get the required fields for each citation type.

        Returns:
            Dict[str, List[str]]: Dictionary mapping citation types to their required fields.
                                 Returns a deep copy to prevent external modification.
        """
        return copy.deepcopy(self._required_for_citation_types)

    def get_required_fields(self, citation_type: str) -> List[str]:
        """
        Get required fields for a specific citation type.
        
        Args:
            citation_type (str): The type of citation
            
        Returns:
            List[str]: List of required fields for the citation type
            
        Raises:
            KeyError: If citation type is not supported
        """
        if citation_type not in self._required_for_citation_types:
            raise KeyError(f"Unsupported citation type: {citation_type}")
        return self._required_for_citation_types[citation_type].copy()

    def get_supported_types(self) -> List[str]:
        """
        Get all supported citation types.

        Returns:
            List[str]: List of supported citation types (book, article, website, report)
        """
        return list(self._required_for_citation_types.keys())

    def is_valid_type(self, citation_type: str) -> bool:
        """
        Check if a citation type is supported.

        Args:
            citation_type (str): The citation type to validate

        Returns:
            bool: True if the citation type is supported, False otherwise
        """
        return citation_type in self._required_for_citation_types


# Global instance for easy access
_config_instance = CitationFieldsConfig()
