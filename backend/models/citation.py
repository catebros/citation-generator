from sqlalchemy import Column, Integer, String, Text, DateTime
from datetime import datetime, UTC
from models.base import Base
import json
import re

class Citation(Base):
    __tablename__ = "citations"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(String, nullable=False)  
    title = Column(String, nullable=False)
    authors = Column(Text, nullable=False)  
    year = Column(Integer, nullable=False)
    publisher = Column(String, nullable=True)
    journal = Column(String, nullable=True)
    volume = Column(String, nullable=True)
    issue = Column(String, nullable=True)
    pages = Column(String, nullable=True)
    doi = Column(String, nullable=True)
    url = Column(String, nullable=True)
    access_date = Column(String, nullable=True)
    place = Column(String, nullable=True)
    edition = Column(String, nullable=True)
    thesis_type = Column(String, nullable=True)  # For thesis/report types
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(UTC))

    def generate_citation(self, format_type: str = "apa") -> str:
        """
        Generate formatted citation based on citation type and format.
        
        Args:
            format_type: Citation format (currently only "apa" supported)
            
        Returns:
            str: Formatted citation string
        """
        format_type = format_type.lower()
        
        if format_type == "apa":
            return self._generate_apa_citation()
        else:
            raise ValueError(f"Unsupported format: {format_type}. Only 'apa' is currently supported.")

    def _normalize_author_name(self, author: str) -> str:
        """Convert author name to APA format with initials.
        Examples: 'John Smith' -> 'Smith, J.', 'Smith, John' -> 'Smith, J.'
        """
        author = author.strip()
        if not author:
            return ""
        
        # If already in format "Last, F.", return as is
        if ',' in author and len(author.split(',')) == 2:
            last, first = author.split(',', 1)
            first = first.strip()
            # Check if first part is already initials
            if len(first) <= 3 and '.' in first:
                return author
            # Convert first name to initials
            initials = '. '.join([name[0].upper() for name in first.split() if name]) + '.'
            return f"{last.strip()}, {initials}"
        
        # If in format "First Last", convert to "Last, F."
        parts = author.split()
        if len(parts) >= 2:
            first_names = parts[:-1]
            last_name = parts[-1]
            initials = '. '.join([name[0].upper() for name in first_names]) + '.'
            return f"{last_name}, {initials}"
        
        # Single name, return as is
        return author

    def _normalize_edition(self, edition: str) -> str:
        """Normalize edition format for APA style.
        Examples: 'second edition' -> '2nd ed.', '3' -> '3rd ed.'
        """
        if not edition:
            return ""
        
        edition = edition.lower().strip()
        
        # If already in correct format, return as is
        if edition.endswith('ed.') and any(edition.startswith(num) for num in ['1st', '2nd', '3rd', '4th', '5th', '6th', '7th', '8th', '9th']):
            return edition
        
        # Handle written-out numbers
        number_mapping = {
            'first': '1st', 'second': '2nd', 'third': '3rd', 'fourth': '4th',
            'fifth': '5th', 'sixth': '6th', 'seventh': '7th', 'eighth': '8th',
            'ninth': '9th', 'tenth': '10th'
        }
        
        for word, num in number_mapping.items():
            if word in edition:
                return f"{num} ed."
        
        # Handle numeric input
        num_match = re.search(r'\d+', edition)
        if num_match:
            num = int(num_match.group())
            if num == 1:
                return ""  # Don't show first edition
            elif num == 2:
                return "2nd ed."
            elif num == 3:
                return "3rd ed."
            elif num in [21, 31, 41, 51, 61, 71, 81, 91]:
                return f"{num}st ed."
            elif num in [22, 32, 42, 52, 62, 72, 82, 92]:
                return f"{num}nd ed."
            elif num in [23, 33, 43, 53, 63, 73, 83, 93]:
                return f"{num}rd ed."
            else:
                return f"{num}th ed."
        
        # If we can't parse it, return as is with "ed." if not present
        if not edition.endswith('ed.'):
            return f"{edition} ed."
        return edition

    def _get_authors_list(self) -> list:
        """Parse authors from JSON string to list."""
        try:
            return json.loads(self.authors) if self.authors else []
        except (json.JSONDecodeError, TypeError):
            return [self.authors] if self.authors else []

    def _format_authors_apa(self, authors: list) -> str:
        """Format authors for APA style with proper initials."""
        if not authors:
            return ""
        
        # Normalize all author names to APA format
        normalized_authors = [self._normalize_author_name(author) for author in authors]
        
        if len(normalized_authors) == 1:
            return normalized_authors[0]
        elif len(normalized_authors) == 2:
            return f"{normalized_authors[0]} & {normalized_authors[1]}"
        else:
            # Three or more authors: use comma separation with & before last
            return ", ".join(normalized_authors[:-1]) + f", & {normalized_authors[-1]}"

    def _generate_apa_citation(self) -> str:
        """Generate APA format citation."""
        authors = self._get_authors_list()
        formatted_authors = self._format_authors_apa(authors)
        
        if self.type == "book":
            return self._generate_apa_book(formatted_authors)
        elif self.type == "article":
            return self._generate_apa_article(formatted_authors)
        elif self.type == "website":
            return self._generate_apa_website(formatted_authors)
        elif self.type == "thesis_report":
            return self._generate_apa_thesis_report(formatted_authors)
        else:
            return f"Unsupported citation type: {self.type}"

    def _generate_apa_book(self, authors: str) -> str:
        """Generate APA book citation."""
        citation_parts = []
        
        if authors:
            # Remove trailing period from authors if present
            authors_clean = authors.rstrip('.')
            citation_parts.append(authors_clean)
        if self.year:
            citation_parts.append(f"({self.year})")
        
        # Title with edition if available
        if self.title:
            title_part = f"*{self.title}*"
            if self.edition and self.edition != "1st":
                # Normalize edition format for APA
                edition_text = self._normalize_edition(self.edition)
                if edition_text:
                    title_part += f" ({edition_text})"
            citation_parts.append(title_part)
        
        if self.publisher:
            citation_parts.append(self.publisher)
        
        if self.doi:
            citation_parts.append(f"https://doi.org/{self.doi}")
            # No final period after DOI
            return ". ".join(citation_parts)
        
        # Join with '. ' and add final period only if no DOI
        if citation_parts:
            result = ". ".join(citation_parts)
            if not result.endswith('.'):
                result += "."
            return result
        return ""

    def _generate_apa_article(self, authors: str) -> str:
        """Generate APA article citation."""
        citation_parts = []
        
        if authors:
            # Remove trailing period from authors if present
            authors_clean = authors.rstrip('.')
            citation_parts.append(authors_clean)
        if self.year:
            citation_parts.append(f"({self.year})")
        # Article titles are NOT in italics in APA
        if self.title:
            citation_parts.append(self.title)
        
        journal_part = ""
        if self.journal:
            # Journal name should be in italics
            journal_part = f"*{self.journal}*"
            if self.volume:
                # Volume should NOT be in separate italics
                journal_part += f", {self.volume}"
                if self.issue:
                    # Issue number in regular text within parentheses
                    journal_part += f"({self.issue})"
            if self.pages:
                # Use en dash for page ranges in APA
                pages_formatted = self.pages.replace('-', '–')
                journal_part += f", {pages_formatted}"
        
        if journal_part:
            citation_parts.append(journal_part)
        
        if self.doi:
            # DOI should not have a trailing period since it's a URL
            citation_parts.append(f"https://doi.org/{self.doi}")
            # Join with '. ' but don't add final period for DOI
            if citation_parts:
                return ". ".join(citation_parts)
        
        # Join with '. ' and ensure proper final punctuation (only if no DOI)
        if citation_parts:
            result = ". ".join(citation_parts)
            if not result.endswith('.'):
                result += "."
            return result
        return ""

    def _generate_apa_website(self, authors: str) -> str:
        """Generate APA website citation."""
        citation_parts = []
        
        if authors:
            # Remove trailing period from authors if present
            authors_clean = authors.rstrip('.')
            citation_parts.append(authors_clean)
        
        # Handle year or n.d. for websites
        if self.year:
            citation_parts.append(f"({self.year})")
        else:
            citation_parts.append("(n.d.)")
        
        if self.title:
            citation_parts.append(self.title)
        
        # For websites, we use the URL directly without "Retrieved from"
        if self.url:
            citation_parts.append(self.url)
            # No final period after URL
            return ". ".join(citation_parts)
        
        # Join with '. ' and add final period only if no URL
        if citation_parts:
            result = ". ".join(citation_parts)
            if not result.endswith('.'):
                result += "."
            return result
        return ""

    def _generate_apa_thesis_report(self, authors: str) -> str:
        """Generate APA thesis/report citation."""
        citation_parts = []
        
        if authors:
            # Remove trailing period from authors if present
            authors_clean = authors.rstrip('.')
            citation_parts.append(authors_clean)
        if self.year:
            citation_parts.append(f"({self.year})")
        if self.title:
            # Title with thesis type specification
            title_part = f"*{self.title}*"
            # Get thesis type from thesis_type field or default to "Doctoral dissertation"
            thesis_type = getattr(self, 'thesis_type', None) or "Doctoral dissertation"
            # Add institution if available
            if self.publisher:
                title_part += f" ({thesis_type}, {self.publisher})"
            else:
                title_part += f" ({thesis_type})"
            citation_parts.append(title_part)
        elif self.publisher:
            # If no title but have publisher, add it separately
            citation_parts.append(self.publisher)
        
        if self.doi:
            citation_parts.append(f"https://doi.org/{self.doi}")
            # No final period after DOI
            return ". ".join(citation_parts)
        
        # Join with '. ' and add final period only if no DOI
        if citation_parts:
            result = ". ".join(citation_parts)
            if not result.endswith('.'):
                result += "."
            return result
        return ""