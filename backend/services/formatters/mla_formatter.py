from .base_citation_formatter import BaseCitationFormatter
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from models.citation import Citation

class MLAFormatter(BaseCitationFormatter):
    """MLA citation formatter implementation."""
    
    def format_citation(self) -> str:
        """Generate MLA format citation."""
        authors = self.get_authors_list()
        formatted_authors = self.format_authors_mla(authors)
        
        if self.citation.type == "book":
            return self.format_book(formatted_authors)
        elif self.citation.type == "article":
            return self.format_article(formatted_authors)
        elif self.citation.type == "website":
            return self.format_website(formatted_authors)
        elif self.citation.type == "report":
            return self.format_report(formatted_authors)
        else:
            return f"Unsupported citation type: {self.citation.type}"
    
    def format_authors_mla(self, authors: list) -> str:
        """Format authors for MLA style."""
        if not authors:
            return ""
        
        # Normalize all author names to MLA format
        normalized_authors = [self._normalize_author_name_mla(author) for author in authors]
        
        if len(normalized_authors) == 1:
            return normalized_authors[0]
        elif len(normalized_authors) == 2:
            # First author: Last, First; Second author: First Last
            return f"{normalized_authors[0]}, and {self._reverse_name(normalized_authors[1])}"
        else:
            # First author: Last, First; Others: First Last
            others = [self._reverse_name(author) for author in normalized_authors[1:]]
            return f"{normalized_authors[0]}, {', '.join(others[:-1])}, and {others[-1]}"
    
    def _normalize_author_name_mla(self, author: str) -> str:
        """Convert author name to MLA format.
        First author: 'Last, First'
        Other authors: 'First Last'
        """
        author = author.strip()
        if not author:
            return ""
        
        # Format "First Last" to "Last, First"
        parts = author.split()
        if len(parts) >= 2:
            first_names = parts[:-1]
            last_name = parts[-1]
            first_name_str = ' '.join(first_names)
            return f"{last_name}, {first_name_str}"
        
        # Single name, return as is
        return author
    
    def _reverse_name(self, name: str) -> str:
        """Convert 'Last, First' back to 'First Last' for non-first authors."""
        if ', ' in name:
            last, first = name.split(', ', 1)
            return f"{first} {last}"
        return name
    
    def format_book(self, authors: str) -> str:
        """Generate MLA book citation.
        Format: Author, First Name. Title of Book. Edition (if not first), Publisher, Year.
        """
        citation_parts = []
        
        if authors:
            citation_parts.append(f"{authors}.")
        
        # Title in italics
        if self.citation.title:
            citation_parts.append(f"*{self.citation.title}*.")
        
        # Edition (if not first)
        if self.citation.edition and self.citation.edition != 1:
            edition_text = self.normalize_edition(self.citation.edition)
            if edition_text:
                citation_parts.append(f"{edition_text},")
        
        # Publisher
        if self.citation.publisher:
            citation_parts.append(f"{self.citation.publisher},")
        
        # Year
        if self.citation.year:
            citation_parts.append(f"{self.citation.year}.")
        else:
            citation_parts.append("n.d.")
        
        return " ".join(citation_parts)
    
    def format_article(self, authors: str) -> str:
        """Generate MLA article citation.
        Format: Author(s). "Title of Article." Journal Name, vol. #, no. #, Year, pp. xxx–xxx. DOI/URL.
        """
        citation_parts = []
        
        if authors:
            citation_parts.append(f"{authors}.")
        
        # Article title in quotes
        if self.citation.title:
            citation_parts.append(f'"{self.citation.title}."')
        
        # Journal name in italics
        journal_part = []
        if self.citation.journal:
            journal_part.append(f"*{self.citation.journal}*")
            
            if self.citation.volume:
                vol_issue = f"vol. {self.citation.volume}"
                if self.citation.issue:
                    vol_issue += f", no. {self.citation.issue}"
                journal_part.append(vol_issue)
            
            if self.citation.year:
                journal_part.append(str(self.citation.year))
            else:
                journal_part.append("n.d.")
            
            if self.citation.pages:
                pages_formatted = self.citation.pages.replace('-', '–')
                journal_part.append(f"pp. {pages_formatted}")
        
        if journal_part:
            citation_parts.append(", ".join(journal_part) + ".")
        
        # DOI or URL – should always be the last element, ending with a point
        if self.citation.doi:
            citation_parts.append(f"https://doi.org/{self.citation.doi}.")
        elif self.citation.url:
            citation_parts.append(f"{self.citation.url}.")
        
        return " ".join(citation_parts)

        
    def format_website(self, authors: str) -> str:
        """Generate MLA website citation.
        Con fecha: Author. "Title of Webpage." Website Name, Date, URL.
        Sin fecha: Author. "Title of Webpage." Website Name, URL. Accessed Day Month Year.
        """
        citation_parts = []
        
        if authors:
            citation_parts.append(f"{authors}.")
        
        # Title in quotes
        if self.citation.title:
            citation_parts.append(f'"{self.citation.title}."')
        
        # Website name in italics
        if self.citation.publisher:
            website_part = f"*{self.citation.publisher}*"
            citation_parts.append(f"{website_part},")
        
        # With publication date
        if self.citation.year:
            citation_parts.append(f"{self.citation.year},")
            if self.citation.url:
                citation_parts.append(f"{self.citation.url}.")
        else:
            # Without publication date -> include access date
            if self.citation.url:
                citation_parts.append(f"{self.citation.url}.")
            if self.citation.access_date:
                citation_parts.append(f"Accessed {self.citation.access_date}.")
            else:
                citation_parts.append("Accessed [Date].")
        
        return " ".join(citation_parts)

    
    def format_report(self, authors: str) -> str:
        """Generate MLA report citation.
        Format: Author. *Title of Report*. Institution/Publisher, Year. URL.
        """
        citation_parts = []
        
        if authors:
            citation_parts.append(f"{authors}.")
        
        # Title in italics
        if self.citation.title:
            citation_parts.append(f"*{self.citation.title}*.")
        
        # Institution/Publisher + Year (grouped to avoid double commas)
        if self.citation.publisher:
            pub_year = self.citation.publisher
            if self.citation.year:
                pub_year += f", {self.citation.year}"
            else:
                pub_year += ", n.d."
            citation_parts.append(f"{pub_year}.")
        
        # URL
        if self.citation.url:
            citation_parts.append(f"{self.citation.url}.")
        
        return " ".join(citation_parts)
