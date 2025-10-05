# backend/services/formatters/mla_formatter.py
from .base_citation_formatter import BaseCitationFormatter
from typing import TYPE_CHECKING, List
from datetime import datetime
from models.citation import Citation

class MLAFormatter(BaseCitationFormatter):
    """
    MLA (Modern Language Association) citation formatter implementation.

    This class implements citation formatting according to MLA 9th edition guidelines.
    It handles all citation types (book, article, website, report) with proper
    formatting including title case, author name formatting, and specific
    punctuation and ordering rules defined by MLA style.

    Attributes:
        _citation (Citation): The citation object to be formatted (inherited from base class)
    """

    def __init__(self, citation: 'Citation'):
        """
        Initialize MLA formatter with citation data.

        Args:
            citation (Citation): The citation object containing all citation fields
        """
        super().__init__(citation)

    def _to_title_case(self, title: str) -> str:
        """
        Convert title to MLA Title Case format (9th edition).

        MLA title case capitalizes:
        - All major words (nouns, verbs, adjectives, adverbs)
        - First and last words always
        - Words after colons (subtitles)

        MLA title case does NOT capitalize (unless first/last):
        - Articles (a, an, the)
        - Prepositions (of, in, on, at, by, for, with, etc.)
        - Coordinating conjunctions (and, or, but, nor, for, so, yet)

        Args:
            title (str): Original title text

        Returns:
            str: Title converted to title case

        Examples:
            "the psychology of learning" -> "The Psychology of Learning"
            "understanding the world: a guide" -> "Understanding the World: A Guide"
            "research in modern times" -> "Research in Modern Times"

        Note:
            - First and last words are always capitalized
            - Handles colons for subtitle capitalization
            - Preserves punctuation
        """
        if not title:
            return ""
        
        # Words that should not be capitalized (unless first or last word)
        lowercase_words = {
            # Articles
            'a', 'an', 'the',

            # Coordinating conjunctions
            'and', 'or', 'but', 'nor', 'for', 'so', 'yet',

            # Short prepositions (under 5 letters per MLA 9)
            'of', 'in', 'on', 'at', 'by', 'to', 'up', 'as', 'is', 'if', 'be',
            'off', 'out', 'via', 'per', 'pro', 'mid',

            # Common prepositions and conjunctions
            'with', 'from', 'into', 'over', 'upon', 'onto', 'than', 'like',
            'till', 'past', 'near', 'down', 'amid', 'atop',

            # Special abbreviations and versus
            'vs', 'vs.', 'v.', 'v',

            # To be verbs (when used as helping verbs)
            'am', 'are', 'was', 'were', 'been', 'being',

            # Other common function words
            'can', 'may', 'must', 'will', 'shall', 'do', 'did', 'does',
            'has', 'have', 'had', 'could', 'would', 'should', 'might'
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
        """
        Generate MLA format citation based on citation type.

        Routes the citation to the appropriate type-specific formatter method
        (book, article, website, or report).

        Returns:
            str: Complete formatted MLA citation with HTML markup

        Note:
            - Returns error message for unsupported citation types
            - Formatted citations include HTML <i> tags for italics
        """
        authors = self._get_authors_list()
        formatted_authors = self._format_authors(authors)
        
        if self._citation.type == "book":
            return self._format_book(formatted_authors)
        elif self._citation.type == "article":
            return self._format_article(formatted_authors)
        elif self._citation.type == "website":
            return self._format_website(formatted_authors)
        elif self._citation.type == "report":
            return self._format_report(formatted_authors)
        else:
            return f"Unsupported citation type: {self._citation.type}"
    
    def _format_authors(self, authors: List[str]) -> str:
        """
        Format authors list according to MLA 9th edition rules.

        MLA author formatting rules:
        - 1 author: Last, First
        - 2 authors: Last, First, and First Last
        - 3 authors: Last, First, First Last, and First Last
        - 4+ authors: Last, First, et al.

        Args:
            authors (list): List of author names in "First Last" format

        Returns:
            str: Formatted authors string with proper punctuation and conjunctions

        Note:
            - Only first author is inverted to "Last, First"
            - Subsequent authors remain in "First Last" format
            - Uses "and" (not ampersand) before last author
            - For 4+ authors, uses "et al." after first author
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
        """
        Convert author name to MLA format for the first author.

        Transforms the first author name from "First Last" format to MLA style
        "Last, First" format. Only used for the first author in MLA citations.

        Args:
            author (str): Author name in "First Last" or "First Middle Last" format

        Returns:
            str: Author name in MLA format "Last, First" or "Last, First Middle"

        Examples:
            "John Smith" -> "Smith, John"
            "John Paul Jones" -> "Jones, John Paul"
            "Smith" -> "Smith"

        Note:
            - Only first author is inverted in MLA style
            - All first/middle names remain after the comma
            - Single-name authors are returned as-is
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
        """
        Convert YYYY-MM-DD format to MLA access date format.

        MLA access date format: "Accessed Day Mon. Year"

        Args:
            date_str (str): Date in YYYY-MM-DD format

        Returns:
            str: Formatted access date in MLA style

        Examples:
            "2025-10-02" -> "Accessed 2 Oct. 2025"
            "2024-01-15" -> "Accessed 15 Jan. 2024"

        Note:
            - Day has no leading zero
            - Month is abbreviated with period (except May)
            - Returns fallback string if date parsing fails
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
        """
        Generate MLA format book citation.

        MLA book format: Author. Title. Edition, Publisher, Year.

        Args:
            authors (str): Pre-formatted authors string

        Returns:
            str: Complete MLA book citation

        Note:
            - Title is italicized and in title case
            - Edition shown only if not first edition
            - Year defaults to "n.d." if not provided
            - All elements separated by commas and periods
        """
        citation_parts = []
        
        if authors:
            citation_parts.append(f"{authors}.")
        
        # Title in italics with Title Case
        if self._citation.title:
            title_case = self._to_title_case(self._citation.title)
            citation_parts.append(f"<i>{title_case}</i>.")
        
        # Edition (if not first)
        if self._citation.edition and self._citation.edition != 1:
            edition_text = self._normalize_edition(self._citation.edition)
            if edition_text:
                citation_parts.append(f"{edition_text},")
        
        # Publisher
        if self._citation.publisher:
            citation_parts.append(f"{self._citation.publisher},")
        
        # Year
        if self._citation.year:
            citation_parts.append(f"{self._citation.year}.")
        else:
            citation_parts.append("n.d.")
        
        return " ".join(citation_parts)
    
    def _format_article(self, authors: str) -> str:
        """
        Generate MLA format article citation.

        MLA article format: Author. "Article Title." Journal Name, vol. #, no. #, Year, pp. xxx-xxx. DOI/URL

        Args:
            authors (str): Pre-formatted authors string

        Returns:
            str: Complete MLA article citation

        Note:
            - Article title in quotes with title case
            - Journal name italicized with title case
            - Volume and issue numbers with "vol." and "no." labels
            - Pages with "pp." prefix
            - DOI or URL at end with no final period
        """
        citation_parts = []
        
        if authors:
            citation_parts.append(f"{authors}.")
        
        # Article title in quotes with Title Case
        if self._citation.title:
            title_case = self._to_title_case(self._citation.title)
            citation_parts.append(f'"{title_case}."')
        
        # Journal name in italics
        journal_part = []
        if self._citation.journal:
            journal_title_case = self._to_title_case(self._citation.journal)
            journal_part.append(f"<i>{journal_title_case}</i>")
            
            if self._citation.volume:
                vol_issue = f"vol. {self._citation.volume}"
                if self._citation.issue:
                    vol_issue += f", no. {self._citation.issue}"
                journal_part.append(vol_issue)
            
            if self._citation.year:
                journal_part.append(str(self._citation.year))
            else:
                journal_part.append("n.d.")
            
            if self._citation.pages:
                pages_formatted = self._citation.pages.replace('-', '–')
                journal_part.append(f"pp. {pages_formatted}")
        
        if journal_part:
            citation_parts.append(", ".join(journal_part) + ".")
        
        # DOI or URL – should always be the last element, NO period at end
        if self._citation.doi:
            citation_parts.append(f"https://doi.org/{self._citation.doi}")
        elif self._citation.url:
            citation_parts.append(f"{self._citation.url}")
        
        return " ".join(citation_parts)

        
    def _format_website(self, authors: str) -> str:
        """
        Generate MLA format website citation.

        MLA website format varies based on publication date:
        - With date: Author. "Page Title." Website Name, Year, URL.
        - Without date: Author. "Page Title." Website Name, URL. Accessed Date.

        Args:
            authors (str): Pre-formatted authors string

        Returns:
            str: Complete MLA website citation

        Note:
            - Page title in quotes with title case
            - Website name (publisher) italicized with title case
            - If no publication year, access date is required
            - URL has no final period if it's last element
        """
        citation_parts = []
        
        if authors:
            citation_parts.append(f"{authors}.")
        
        # Title in quotes with Title Case
        if self._citation.title:
            title_case = self._to_title_case(self._citation.title)
            citation_parts.append(f'"{title_case}."')
        
        # Website name in italics with Title Case
        if self._citation.publisher:
            publisher_title_case = self._to_title_case(self._citation.publisher)
            website_part = f"<i>{publisher_title_case}</i>"
            citation_parts.append(f"{website_part},")
        
        # With publication date
        if self._citation.year:
            citation_parts.append(f"{self._citation.year},")
            if self._citation.url:
                citation_parts.append(f"{self._citation.url}")
        else:
            # Without publication date -> include access date
            if self._citation.url:
                citation_parts.append(f"{self._citation.url}.")
            if self._citation.access_date:
                formatted_date = self._format_access_date(self._citation.access_date)
                citation_parts.append(f"{formatted_date}.")
            else:
                citation_parts.append("Accessed [Date].")
        
        return " ".join(citation_parts)

    
    def _format_report(self, authors: str) -> str:
        """
        Generate MLA format report citation.

        MLA report format: Author. Title. Institution, Year. URL

        Args:
            authors (str): Pre-formatted authors string

        Returns:
            str: Complete MLA report citation

        Note:
            - Title is italicized and in title case
            - Institution (publisher) and year combined with comma
            - Year defaults to "n.d." if not provided
            - URL has no final period
        """
        citation_parts = []
        
        if authors:
            citation_parts.append(f"{authors}.")
        
        # Title in italics with Title Case
        if self._citation.title:
            title_case = self._to_title_case(self._citation.title)
            citation_parts.append(f"<i>{title_case}</i>.")
        
        # Institution/Publisher + Year (grouped to avoid double commas)
        if self._citation.publisher:
            pub_year = self._citation.publisher
            if self._citation.year:
                pub_year += f", {self._citation.year}"
            else:
                pub_year += ", n.d."
            citation_parts.append(f"{pub_year}.")
        
        # URL without period at end
        if self._citation.url:
            citation_parts.append(f"{self._citation.url}")
        
        return " ".join(citation_parts)
