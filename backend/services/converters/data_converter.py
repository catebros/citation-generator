# backend/services/converters/data_converter.py
"""Data serialization and conversion logic following SRP."""

from datetime import date
from typing import Any, Dict, List
import json


class DataConverter:
    """Centralized data serialization and conversion methods."""
    
    @staticmethod
    def serialize_citation_data(data: Dict[str, Any]) -> Dict[str, Any]:
        """Convert citation data types (dates, URLs) to database-compatible formats."""
        serialized = data.copy()
        
        # Convert date objects to strings
        if serialized.get('access_date'):
            if isinstance(serialized['access_date'], date):
                serialized['access_date'] = serialized['access_date'].strftime('%Y-%m-%d')
        
        # Convert URLs to strings
        if serialized.get('url'):
            serialized['url'] = str(serialized['url'])
        
        return serialized
    
    @staticmethod
    def convert_authors_to_dict(authors_json: str) -> List[Dict[str, str]]:
        """Convert JSON authors string to dictionary format."""
        if not authors_json:
            return []
        
        try:
            if isinstance(authors_json, str):
                return json.loads(authors_json)
            return authors_json
        except (json.JSONDecodeError, TypeError):
            return []
    
    @staticmethod
    def merge_search_data(merged_data: Dict[str, Any]) -> Dict[str, Any]:
        """Format data for search operations by converting authors from JSON to list."""
        search_data = {}
        for key, value in merged_data.items():
            if key == "authors" and isinstance(value, str):
                # Convert JSON string back to list for the search
                search_data[key] = json.loads(value) if value else []
            else:
                search_data[key] = value
        
        return search_data
