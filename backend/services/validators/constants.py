# backend/services/validators/constants.py

SUPPORTED_FORMATS = ["apa", "mla"]
DEFAULT_FORMAT = "apa"
DATE_FORMAT = "%Y-%m-%d"

# Citation type configuration mapping
CITATION_TYPES_CONFIG = {
    "book": {
        "required": ["type", "title", "authors", "year", "publisher", "place"],
        "valid": ["type", "title", "authors", "year", "publisher", "place", "edition"],
    },
    "article": {
        "required": ["type", "title", "authors", "year", "journal", "volume", "pages"],
        "valid": [
            "type",
            "title",
            "authors",
            "year",
            "journal",
            "volume",
            "issue",
            "pages",
            "doi",
        ],
    },
    "website": {
        "required": [
            "type",
            "title",
            "authors",
            "year",
            "publisher",
            "url",
            "access_date",
        ],
        "valid": [
            "type",
            "title",
            "authors",
            "year",
            "publisher",
            "url",
            "access_date",
        ],
    },
    "report": {
        "required": ["type", "title", "authors", "year", "publisher", "place"],
        "valid": ["type", "title", "authors", "year", "publisher", "url", "place"],
    },
}

# Fields used for serialization in database
SERIALIZATION_FIELDS = {
    "date_fields": ["access_date"],
    "url_fields": ["url"],
    "json_fields": ["authors"],
}
