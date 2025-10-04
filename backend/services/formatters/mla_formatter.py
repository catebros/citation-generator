# backend/services/formatters/mla_formatter.py
from .base_citation_formatter import BaseCitationFormatter
from typing import TYPE_CHECKING
from datetime import datetime

if TYPE_CHECKING:
    from models.citation import Citation

class MLAFormatter(BaseCitationFormatter):
    """MLA citation formatter implementation."""
    
    def _to_title_case(self, title: str) -> str:
        """Convert title to MLA Title Case format.
        
        Rules:
        - Capitalize all major words
        - Don't capitalize articles, prepositions, or short conjunctions 
          (a, an, the, of, in, on, at, by, for, with, etc.) unless they are 
          the first or last word of the title
        - Capitalize words after colons
        """
        if not title:
            return ""
        
        # Words that should not be capitalized (unless first or last word)
        lowercase_words = {
            'a', 'an', 'the', 'and', 'or', 'but', 'nor', 'for', 'so', 'yet',
            'of', 'in', 'on', 'at', 'by', 'to', 'up', 'as', 'is', 'if', 'be',
            'with', 'from', 'into', 'over', 'upon', 'onto', 'than', 'like',
            'via', 'per', 'vs', 'vs.', 'v.', 'v'
        }
        
        # Split by colon to handle subtitles
        parts = title.split(':')
        processed_parts = []
        
        for part in parts:
            words = part.strip().split()
            if not words:
                processed_parts.append("")
                continue
            
            title_case_words = []
            
            for i, word in enumerate(words):
                # Remove punctuation for checking, but keep it for the final word
                clean_word = word.strip('.,;:!?"()[]{}').lower()
                
                # Always capitalize first and last word of each part
                if i == 0 or i == len(words) - 1:
                    title_case_words.append(word.capitalize())
                # Check if word should remain lowercase
                elif clean_word in lowercase_words:
                    title_case_words.append(word.lower())
                else:
                    title_case_words.append(word.capitalize())
            
            processed_parts.append(' '.join(title_case_words))
        
        return ': '.join(processed_parts)
    
    def format_citation(self) -> str:
        """Generate MLA format citation."""
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
        """Format authors for MLA style.
        MLA rules:
        - 1 author: Last, First
        - 2 authors: Last, First, and First Last
        - 3 authors: Last, First, First Last, and First Last
        - 4+ authors: Last, First, et al.
        """
        if not authors:
            return ""
        
        # First author is always in "Last, First" format
        first_author = self._normalize_author_name(authors[0])
        
        if len(authors) == 1:
            return first_author
        elif len(authors) == 2:
            # First author: Last, First; Second author: First Last (keep original format)
            second_author = authors[1].strip()
            return f"{first_author}, and {second_author}"
        elif len(authors) == 3:
            # Three authors: First author: Last, First; Others: First Last (keep original format)
            second_author = authors[1].strip()
            third_author = authors[2].strip()
            return f"{first_author}, {second_author}, and {third_author}"
        else:
            # 4+ authors: First author + et al.
            return f"{first_author}, et al."
    
    def _normalize_author_name(self, author: str) -> str:
        """Convert author name to MLA format for the first author.
        Converts 'First Last' to 'Last, First'
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
    
    def _format_access_date(self, date_str: str) -> str:
        """Convert YYYY-MM-DD format to MLA format: Accessed Day Mon. Year.
        Example: '2025-10-02' -> 'Accessed 2 Oct. 2025'
        """
        try:
            dt = datetime.strptime(date_str, "%Y-%m-%d")
            # Format with day without leading zero, abbreviated month with period, year
            day = str(dt.day)  # Remove leading zero
            month_map = {
                1: 'Jan.', 2: 'Feb.', 3: 'Mar.', 4: 'Apr.', 
                5: 'May', 6: 'Jun.', 7: 'Jul.', 8: 'Aug.',
                9: 'Sep.', 10: 'Oct.', 11: 'Nov.', 12: 'Dec.'
            }
            month = month_map[dt.month]
            year = str(dt.year)
            return f"Accessed {day} {month} {year}"
        except ValueError:
            # Fallback if date format is not as expected
            return f"Accessed {date_str}"
    
    def _format_book(self, authors: str) -> str:
        """Generate MLA book citation.
        Format: Author, First Name. Title of Book. Edition (if not first), Publisher, Year.
        """
        citation_parts = []
        
        if authors:
            citation_parts.append(f"{authors}.")
        
        # Title in italics with Title Case
        if self.citation.title:
            title_case = self._to_title_case(self.citation.title)
            citation_parts.append(f"<i>{title_case}</i>.")
        
        # Edition (if not first)
        if self.citation.edition and self.citation.edition != 1:
            edition_text = self._normalize_edition(self.citation.edition)
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
    
    def _format_article(self, authors: str) -> str:
        """Generate MLA article citation.
        Format: Author(s). "Title of Article." Journal Name, vol. #, no. #, Year, pp. xxx–xxx. DOI/URL.
        """
        citation_parts = []
        
        if authors:
            citation_parts.append(f"{authors}.")
        
        # Article title in quotes with Title Case
        if self.citation.title:
            title_case = self._to_title_case(self.citation.title)
            citation_parts.append(f'"{title_case}."')
        
        # Journal name in italics
        journal_part = []
        if self.citation.journal:
            journal_title_case = self._to_title_case(self.citation.journal)
            journal_part.append(f"<i>{journal_title_case}</i>")
            
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
        
        # DOI or URL – should always be the last element, NO period at end
        if self.citation.doi:
            citation_parts.append(f"https://doi.org/{self.citation.doi}")
        elif self.citation.url:
            citation_parts.append(f"{self.citation.url}")
        
        return " ".join(citation_parts)

        
    def _format_website(self, authors: str) -> str:
        """Generate MLA website citation.
        Con fecha: Author. "Title of Webpage." Website Name, Date, URL.
        Sin fecha: Author. "Title of Webpage." Website Name, URL. Accessed Day Month Year.
        """
        citation_parts = []
        
        if authors:
            citation_parts.append(f"{authors}.")
        
        # Title in quotes with Title Case
        if self.citation.title:
            title_case = self._to_title_case(self.citation.title)
            citation_parts.append(f'"{title_case}."')
        
        # Website name in italics with Title Case
        if self.citation.publisher:
            publisher_title_case = self._to_title_case(self.citation.publisher)
            website_part = f"<i>{publisher_title_case}</i>"
            citation_parts.append(f"{website_part},")
        
        # With publication date
        if self.citation.year:
            citation_parts.append(f"{self.citation.year},")
            if self.citation.url:
                citation_parts.append(f"{self.citation.url}")
        else:
            # Without publication date -> include access date
            if self.citation.url:
                citation_parts.append(f"{self.citation.url}.")
            if self.citation.access_date:
                formatted_date = self._format_access_date(self.citation.access_date)
                citation_parts.append(f"{formatted_date}.")
            else:
                citation_parts.append("Accessed [Date].")
        
        return " ".join(citation_parts)

    
    def _format_report(self, authors: str) -> str:
        """Generate MLA report citation.
        Format: Author. <i>Title of Report</i>. Institution/Publisher, Year. URL.
        """
        citation_parts = []
        
        if authors:
            citation_parts.append(f"{authors}.")
        
        # Title in italics with Title Case
        if self.citation.title:
            title_case = self._to_title_case(self.citation.title)
            citation_parts.append(f"<i>{title_case}</i>.")
        
        # Institution/Publisher + Year (grouped to avoid double commas)
        if self.citation.publisher:
            pub_year = self.citation.publisher
            if self.citation.year:
                pub_year += f", {self.citation.year}"
            else:
                pub_year += ", n.d."
            citation_parts.append(f"{pub_year}.")
        
        # URL without period at end
        if self.citation.url:
            citation_parts.append(f"{self.citation.url}")
        
        return " ".join(citation_parts)
