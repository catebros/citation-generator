# Configuration file for citation types and their required fields

CITATION_TYPES = {
    "book": ["type", "title", "authors", "year", "publisher", "place", "edition"],
    "article": ["type", "title", "authors", "year", "journal", "volume", "issue", "pages", "doi"],
    "website": ["type", "title", "authors", "year", "url", "access_date"],
    "thesis_report": ["type", "title", "authors", "year", "publisher", "place", "doi"]
}

# All possible fields that a citation can have
ALL_FIELDS = [
    "type", "title", "authors", "year", "publisher", "place", "edition",
    "journal", "volume", "issue", "pages", "doi", "url", "access_date"
]
