# backend/services/formatters/apa_formatter.py
from .base_citation_formatter import BaseCitationFormatter
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from models.citation import Citation

class APAFormatter(BaseCitationFormatter):
    """APA citation formatter implementation."""
    
    def format_citation(self) -> str:
        """Generate APA format citation."""
        authors = self._get_authors_list()
        formatted_authors = self._format_authors(authors)
        
        if self.citation.type == "book":
            return self._format_book(formatted_authors)
        elif self.citation.type == "article":
            return self._format_article(formatted_authors)
        elif self.citation.type == "website":
            return self._format_website(formatted_authors)
        elif self.citation.type == "report":
            return self._format_report(formatted_authors)
        else:
            return f"Unsupported citation type: {self.citation.type}"
    
    def _format_authors(self, authors: list) -> str:
        """Format authors for APA style with proper initials.
        APA 7 rules:
        - 1 author: Author, A.
        - 2 authors: Author, A., & Author, B.
        - 3-20 authors: Author, A., Author, B., & Author, C.
        - 21+ authors: Author, A., Author, B., ..., & Author, Z.
        """
        if not authors:
            return ""
        
        # Normalize all author names to APA format
        normalized_authors = [self._normalize_author_name(author) for author in authors]
        
        if len(normalized_authors) == 1:
            return normalized_authors[0]
        elif len(normalized_authors) == 2:
            return f"{normalized_authors[0]}, & {normalized_authors[1]}"
        elif len(normalized_authors) <= 20:
            # 3-20 authors: use comma separation with & before last
            return ", ".join(normalized_authors[:-1]) + f", & {normalized_authors[-1]}"
        else:
            # 21+ authors: first 19 + "..." + last author (APA 7 rule)
            first_19 = ", ".join(normalized_authors[:19])
            last_author = normalized_authors[-1]
            return f"{first_19}, ..., & {last_author}"
    
    def _normalize_author_name(self, author: str) -> str:
        """Convert author name to APA format with initials.
        Examples: 'John Smith' -> 'Smith, J.'
        """
        author = author.strip()
        if not author:
            return ""
        
        # format "First Last", convert to "Last, F."
        parts = author.split()
        if len(parts) >= 2:
            first_names = parts[:-1]
            last_name = parts[-1]
            initials = '. '.join([name[0].upper() for name in first_names]) + '.'
            return f"{last_name}, {initials}"
        
        # Single name, return as is
        return author
    
    def _format_book(self, authors: str) -> str:
        """Generate APA book citation."""
        citation_parts = []
        
        if authors:
            # Remove trailing period from authors if present
            authors_clean = authors.rstrip('.')
            citation_parts.append(authors_clean)
        
        # Handle year or n.d.
        if self.citation.year:
            citation_parts.append(f"({self.citation.year})")
        else:
            citation_parts.append("(n.d.)")
        
        # Title with edition if available
        if self.citation.title:
            title_part = f"<i>{self.citation.title}</i>"
            if self.citation.edition and self.citation.edition != 1:
                # Normalize edition format for APA
                edition_text = self._normalize_edition(self.citation.edition)
                if edition_text:
                    title_part += f" ({edition_text})"
            citation_parts.append(title_part)
        
        if self.citation.publisher:
            citation_parts.append(self.citation.publisher)
        
        # Join with '. ' and add final period only if no DOI
        if citation_parts:
            result = ". ".join(citation_parts)
            if not result.endswith('.'):
                result += "."
            return result
        return ""
    
    def _format_article(self, authors: str) -> str:
        """Generate APA article citation."""
        citation_parts = []
        
        if authors:
            # Remove trailing period from authors if present
            authors_clean = authors.rstrip('.')
            citation_parts.append(authors_clean)
        
        # Handle year or n.d.
        if self.citation.year:
            citation_parts.append(f"({self.citation.year})")
        else:
            citation_parts.append("(n.d.)")
            
        # Article titles are NOT in italics in APA
        if self.citation.title:
            citation_parts.append(self.citation.title)
        
        journal_part = ""
        if self.citation.journal:
            # Journal name should be in italics
            journal_part = f"<i>{self.citation.journal}</i>"
            if self.citation.volume:
                # Volume should also be in italics according to APA
                journal_part += f", <i>{self.citation.volume}</i>"
                if self.citation.issue:
                    # Issue number in regular text within parentheses
                    journal_part += f"({self.citation.issue})"
            if self.citation.pages:
                # Use en dash for page ranges in APA
                pages_formatted = self.citation.pages.replace('-', '–')
                journal_part += f", {pages_formatted}"
        
        if journal_part:
            citation_parts.append(journal_part)
        
        if self.citation.doi:
            # DOI should not have a trailing period since it's a URL
            citation_parts.append(f"https://doi.org/{self.citation.doi}")
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
    
    def _format_website(self, authors: str) -> str:
        """Generate APA website citation."""
        citation_parts = []
        
        if authors:
            # Remove trailing period from authors if present
            authors_clean = authors.rstrip('.')
            citation_parts.append(authors_clean)
        
        # Handle year or n.d. for websites
        if self.citation.year:
            citation_parts.append(f"({self.citation.year})")
        else:
            citation_parts.append("(n.d.)")
        
        if self.citation.title:
            citation_parts.append(self.citation.title)
        
        # Add website name (publisher field) - Nombre del sitio
        if self.citation.publisher:
            citation_parts.append(f"<i>{self.citation.publisher}</i>")
        
        # For websites, we use the URL directly without "Retrieved from"
        if self.citation.url:
            citation_parts.append(self.citation.url)
            # No final period after URL
            return ". ".join(citation_parts)
        
        # Join with '. ' and add final period only if no URL
        if citation_parts:
            result = ". ".join(citation_parts)
            if not result.endswith('.'):
                result += "."
            return result
        return ""
    
    def _format_report(self, authors: str) -> str:
        """Generate APA report citation."""
        citation_parts = []
        
        if authors:
            # Remove trailing period from authors if present
            authors_clean = authors.rstrip('.')
            citation_parts.append(authors_clean)
        
        # Handle year or n.d.
        if self.citation.year:
            citation_parts.append(f"({self.citation.year})")
        else:
            citation_parts.append("(n.d.)")
            
        if self.citation.title:
            # Title with report type specification
            title_part = f"<i>{self.citation.title}</i> [Report]"
            citation_parts.append(title_part)
        
        # Add institution/organization (publisher)
        if self.citation.publisher:
            citation_parts.append(self.citation.publisher)
        
        # Add URL if available (reports don't have DOI)
        if self.citation.url:
            citation_parts.append(self.citation.url)
            # No final period after URL
            return ". ".join(citation_parts)
        
        # Join with '. ' and add final period only if no URL
        if citation_parts:
            result = ". ".join(citation_parts)
            if not result.endswith('.'):
                result += "."
            return result
        return ""