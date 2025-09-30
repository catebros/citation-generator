# Configuration file for citation types and their required fields

REQUIRED_FOR_CITATION_TYPES = {
    "book": ["type", "title", "authors", "year", "publisher", "place", "edition"],
    "article": ["type", "title", "authors", "year", "journal", "volume", "issue", "pages", "doi"],
    "website": ["type", "title", "authors", "year", "publisher", "url", "access_date"],
    "report": ["type", "title", "authors", "year", "publisher", "url", "place"]
}

# All possible fields that a citation can have
ALL_FIELDS = [
    "type", "title", "authors", "year", "publisher", "place", "edition",
    "journal", "volume", "issue", "pages", "doi", "url", "access_date"
]
