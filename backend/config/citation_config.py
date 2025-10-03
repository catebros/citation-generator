# backend/config/citation_config.py
from typing import Dict, List


class CitationConfig:
    """
    Singleton class for managing citation configuration.
    This ensures only one instance of the configuration exists throughout the application.
    """
    _instance = None
    _initialized = False

    def __new__(cls):
        """Create a new instance only if one doesn't exist."""
        if cls._instance is None:
            cls._instance = super(CitationConfig, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        """Initialize the configuration data only once."""
        if not self._initialized:
            self._required_for_citation_types = {
                "book": ["type", "title", "authors", "year", "publisher", "place", "edition"],
                "article": ["type", "title", "authors", "year", "journal", "volume", "issue", "pages", "doi"],
                "website": ["type", "title", "authors", "year", "publisher", "url", "access_date"],
                "report": ["type", "title", "authors", "year", "publisher", "url", "place"]
            }
            
            self._all_fields = [
                "type", "title", "authors", "year", "publisher", "place", "edition",
                "journal", "volume", "issue", "pages", "doi", "url", "access_date"
            ]
            
            CitationConfig._initialized = True

    def get_required_for_citation_types(self) -> Dict[str, List[str]]:
        """Get the required fields for each citation type."""
        return self._required_for_citation_types.copy()

    def get_all_fields(self) -> List[str]:
        """Get all possible citation fields."""
        return self._all_fields.copy()

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
        """Get all supported citation types."""
        return list(self._required_for_citation_types.keys())

    def is_valid_field(self, field: str) -> bool:
        """Check if a field is valid for any citation type."""
        return field in self._all_fields

    def is_valid_type(self, citation_type: str) -> bool:
        """Check if a citation type is supported."""
        return citation_type in self._required_for_citation_types


# Global instance for easy access (backwards compatibility)
_config_instance = CitationConfig()

# Backwards compatibility - expose the old interface
REQUIRED_FOR_CITATION_TYPES = _config_instance.get_required_for_citation_types()
ALL_FIELDS = _config_instance.get_all_fields()
