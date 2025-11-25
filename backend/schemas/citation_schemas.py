# backend/schemas/citation_schemas.py
from pydantic import BaseModel, Field, field_validator, model_validator, HttpUrl
from typing import List, Optional, Literal
from datetime import datetime, date
import re

# String length limits for validation
MAX_TITLE_LENGTH = 500
MAX_AUTHOR_NAME_LENGTH = 150
MAX_PUBLISHER_LENGTH = 200
MAX_JOURNAL_LENGTH = 200
MAX_PLACE_LENGTH = 100
MAX_DOI_LENGTH = 300
MAX_PAGES_LENGTH = 50
MAX_ISSUE_LENGTH = 50


class CitationBase(BaseModel):
    """Base schema for citation validation with common fields and validators."""

    type: Literal["book", "article", "website", "report"] = Field(
        ..., description="Citation type: book, article, website, or report"
    )
    title: str = Field(..., min_length=1, max_length=MAX_TITLE_LENGTH, description="Title of the cited work")
    authors: List[str] = Field(..., min_length=1, description="List of author names")
    year: Optional[int] = Field(None, ge=0, description="Publication year")

    # Optional fields for different citation types
    publisher: Optional[str] = Field(None, min_length=1, max_length=MAX_PUBLISHER_LENGTH)
    journal: Optional[str] = Field(None, min_length=1, max_length=MAX_JOURNAL_LENGTH)
    volume: Optional[int] = Field(None, gt=0)
    issue: Optional[str] = Field(None, min_length=1, max_length=MAX_ISSUE_LENGTH)
    pages: Optional[str] = Field(None, max_length=MAX_PAGES_LENGTH)
    doi: Optional[str] = Field(None, max_length=MAX_DOI_LENGTH)
    url: Optional[HttpUrl] = Field(None, description="URL of the resource")
    access_date: Optional[date] = Field(None, description="Access date in YYYY-MM-DD format")
    place: Optional[str] = Field(None, min_length=1, max_length=MAX_PLACE_LENGTH)
    edition: Optional[int] = Field(None, gt=0)

    @field_validator('type')
    @classmethod
    def normalize_type(cls, v: str) -> str:
        """Normalize citation type to lowercase."""
        return v.lower()

    @field_validator('authors')
    @classmethod
    def validate_authors(cls, v: List[str]) -> List[str]:
        """Validate author names - length and allowed characters."""
        for author in v:
            stripped = author.strip()
            if len(stripped) > MAX_AUTHOR_NAME_LENGTH:
                raise ValueError(f"Author name exceeds {MAX_AUTHOR_NAME_LENGTH} characters")
            if not re.match(r"^[a-zA-ZÀ-ÿ\s\-\'\.']+$", stripped):
                raise ValueError("Author names can only contain letters, spaces, hyphens, apostrophes, and periods")
        return v

    @field_validator('year')
    @classmethod
    def validate_year_max(cls, v: Optional[int]) -> Optional[int]:
        """Validate year doesn't exceed current year."""
        if v is not None and v > datetime.now().year:
            raise ValueError(f"Year cannot exceed {datetime.now().year}")
        return v

    @field_validator('doi')
    @classmethod
    def validate_doi_format(cls, v: Optional[str]) -> Optional[str]:
        """Validate DOI format (10.xxxx/xxxx)."""
        if v is not None and not re.match(r'^10\.\d{4,}/.+$', v):
            raise ValueError("Invalid DOI format (expected: 10.xxxx/xxxx)")
        return v

    @field_validator('pages')
    @classmethod
    def validate_pages_format(cls, v: Optional[str]) -> Optional[str]:
        """Validate pages format and range logic (e.g., '123-145' or '1-3, 5-7')."""
        if v is None:
            return v

        # Check pattern
        single_range = r'\d+-\d+'
        if not re.match(rf'^{single_range}(?:\s*,\s*{single_range})*$', v):
            raise ValueError("Pages must be in format 'start-end' or multiple ranges like '1-3, 5-7'")

        # Validate start <= end for each range
        for range_str in v.split(','):
            start, end = map(int, range_str.strip().split('-'))
            if start > end:
                raise ValueError(f"Invalid page range: {range_str.strip()} (start > end)")

        return v


class CitationCreate(CitationBase):
    """Schema for creating a citation with type-specific field requirements."""

    @model_validator(mode='after')
    def validate_required_fields_by_type(self):
        """Validate that all required fields for the citation type are present."""
        # Define required and valid fields for each type
        fields_config = {
            "book": {
                "required": ["type", "title", "authors", "year", "publisher", "place"],
                "valid": ["type", "title", "authors", "year", "publisher", "place", "edition"]
            },
            "article": {
                "required": ["type", "title", "authors", "year", "journal", "volume", "pages"],
                "valid": ["type", "title", "authors", "year", "journal", "volume", "issue", "pages", "doi"]
            },
            "website": {
                "required": ["type", "title", "authors", "year", "publisher", "url", "access_date"],
                "valid": ["type", "title", "authors", "year", "publisher", "url", "access_date"]
            },
            "report": {
                "required": ["type", "title", "authors", "year", "publisher", "place"],
                "valid": ["type", "title", "authors", "year", "publisher", "url", "place"]
            }
        }

        config = fields_config.get(self.type, {})
        required_fields = config.get("required", [])
        valid_fields = config.get("valid", [])

        # Check for missing required fields
        missing = [field for field in required_fields if getattr(self, field, None) is None]
        if missing:
            raise ValueError(f"Missing required {self.type} fields: {', '.join(missing)}")

        # Check for invalid fields (fields not allowed for this type)
        provided_fields = {k for k, v in self.model_dump(exclude_none=False).items() if v is not None}
        invalid_fields = provided_fields - set(valid_fields)
        if invalid_fields:
            raise ValueError(
                f"Invalid fields for {self.type}: {', '.join(invalid_fields)}. "
                f"Valid fields: {', '.join(sorted(valid_fields))}"
            )

        return self


class CitationUpdate(BaseModel):
    """Schema for updating a citation with partial updates allowed."""

    type: Optional[Literal["book", "article", "website", "report"]] = Field(None, description="Citation type")
    title: Optional[str] = Field(None, min_length=1, max_length=MAX_TITLE_LENGTH)
    authors: Optional[List[str]] = Field(None, min_length=1)
    year: Optional[int] = Field(None, ge=0)
    publisher: Optional[str] = Field(None, min_length=1, max_length=MAX_PUBLISHER_LENGTH)
    journal: Optional[str] = Field(None, min_length=1, max_length=MAX_JOURNAL_LENGTH)
    volume: Optional[int] = Field(None, gt=0)
    issue: Optional[str] = Field(None, min_length=1, max_length=MAX_ISSUE_LENGTH)
    pages: Optional[str] = Field(None, max_length=MAX_PAGES_LENGTH)
    doi: Optional[str] = Field(None, max_length=MAX_DOI_LENGTH)
    url: Optional[HttpUrl] = Field(None)
    access_date: Optional[date] = Field(None)
    place: Optional[str] = Field(None, min_length=1, max_length=MAX_PLACE_LENGTH)
    edition: Optional[int] = Field(None, gt=0)

    # Reuse validators from CitationBase
    validate_type = field_validator('type')(CitationBase.normalize_type)
    validate_authors = field_validator('authors')(CitationBase.validate_authors)
    validate_year_max = field_validator('year')(CitationBase.validate_year_max)
    validate_doi_format = field_validator('doi')(CitationBase.validate_doi_format)
    validate_pages_format = field_validator('pages')(CitationBase.validate_pages_format)


class CitationResponse(CitationBase):
    """Schema for citation responses."""

    id: int
    created_at: datetime
    url: Optional[str] = None  # Override to return as string from DB
    access_date: Optional[str] = None  # Override to return as string from DB

    class Config:
        from_attributes = True
