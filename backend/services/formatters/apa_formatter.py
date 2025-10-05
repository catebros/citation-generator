# backend/services/formatters/apa_formatter.py
from .base_citation_formatter import BaseCitationFormatter
from typing import TYPE_CHECKING, List
from models.citation import Citation

class APAFormatter(BaseCitationFormatter):
    """
    APA (American Psychological Association) citation formatter implementation.

    This class implements citation formatting according to APA 7th edition guidelines.
    It handles all citation types (book, article, website, report) with proper
    formatting including sentence case titles, author name formatting with initials,
    and specific punctuation and ordering rules defined by APA style.

    Attributes:
        _citation (Citation): The citation object to be formatted (inherited from base class)
    """

    def __init__(self, citation: 'Citation'):
        """
        Initialize APA formatter with citation data.

        Args:
            citation (Citation): The citation object containing all citation fields
        """
        super().__init__(citation)

    def _to_sentence_case(self, title: str) -> str:
        """
        Convert title to APA Sentence Case format (7th edition).

        APA sentence case capitalizes only:
        - The first word of the title
        - The first word after a colon (subtitle)
        - Proper nouns and known acronyms

        Args:
            title (str): Original title text

        Returns:
            str: Title converted to sentence case

        Examples:
            "The Psychology of Learning" -> "The psychology of learning"
            "AI and ML: Modern Approaches" -> "AI and ML: Modern approaches"
            "Understanding HTTP Protocols" -> "Understanding HTTP protocols"

        Note:
            - Preserves known acronyms (API, AI, ML, HTML, etc.)
            - Handles colons for subtitle capitalization
            - Acronyms of 2-5 uppercase letters are preserved
        """
        if not title:
            return ""
        
        # Known acronyms and abbreviations that should stay uppercase
        acronyms = {
            # Technology & Computing
            'AI', 'API', 'AR', 'AWS', 'CDN', 'CLI', 'CPU', 'CSS', 'CSV', 'DNA', 'DOS', 'DVD',
            'FAQ', 'FTP', 'GIF', 'GPS', 'GPU', 'GUI', 'HTML', 'HTTP', 'HTTPS', 'IDE', 'IoT',
            'IP', 'IT', 'JPEG', 'JPG', 'JS', 'JSON', 'LAN', 'LED', 'ML', 'NLP', 'OS', 'PC',
            'PDF', 'PHP', 'PNG', 'RAM', 'REST', 'RGB', 'ROM', 'SaaS', 'SDK', 'SEO', 'SQL',
            'SSH', 'SSL', 'TCP', 'TLS', 'UI', 'URL', 'USB', 'UX', 'VPN', 'VR', 'WAN', 'WiFi',
            'WWW', 'XML', 'YAML', 'ZIP',

            # Organizations & Institutions
            'CIA', 'FBI', 'FDA', 'NATO', 'NASA', 'NOAA', 'UNESCO', 'UNICEF', 'UN', 'WHO',
            'EU', 'EPA', 'FCC', 'CDC', 'MIT', 'UCLA', 'CUNY', 'NYU', 'USC', 'IEEE',

            # Business & Finance
            'CEO', 'CFO', 'CTO', 'COO', 'CPA', 'LLC', 'IPO', 'GDP', 'SEC', 'IRS', 'NYSE',
            'ATM', 'ETF', 'ROI', 'KPI', 'B2B', 'B2C', 'HR', 'PR', 'RFP', 'SLA',

            # Science & Medicine
            'DNA', 'RNA', 'HIV', 'AIDS', 'MRI', 'CT', 'EEG', 'ECG', 'PCR', 'STEM',
            'ADHD', 'OCD', 'PTSD', 'BMI', 'FDA', 'CDC', 'WHO',

            # Education & Testing
            'ACT', 'SAT', 'GPA', 'GRE', 'GMAT', 'TOEFL', 'IELTS', 'IQ', 'EQ', 'AP', 'IB',
            'PhD', 'MBA', 'BA', 'BS', 'MA', 'MS', 'MD', 'JD', 'EdD', 'DDS',

            # Media & Communication
            'TV', 'DVD', 'CD', 'FM', 'AM', 'PM', 'BBC', 'CNN', 'ESPN', 'HBO', 'NBC',
            'CBS', 'ABC', 'NPR', 'PBS', 'RSS', 'SMS', 'MMS', 'DM',

            # Geography & Countries
            'USA', 'UK', 'UAE', 'EU', 'USSR', 'NYC', 'LA', 'DC', 'SF',

            # Military & Defense
            'FBI', 'CIA', 'NSA', 'DOD', 'RAF', 'USAF', 'NATO', 'ICBM',

            # Miscellaneous
            'FAQ', 'DIY', 'ASAP', 'FYI', 'RSVP', 'TBD', 'TBA', 'ETA', 'OK', 'AWOL',
            'PS', 'vs', 'VS', 'aka', 'AKA', 'etc', 'ETC', 'ie', 'IE', 'eg', 'EG'
        }
        
        # Split by colon to handle subtitles
        parts = title.split(':')
        processed_parts = []
        
        for part_index, part in enumerate(parts):
            part = part.strip()
            if not part:
                processed_parts.append("")
                continue
                
            words = part.split()
            if not words:
                processed_parts.append("")
                continue
            
            sentence_words = []
            for i, word in enumerate(words):
                # Extract punctuation
                punctuation = ""
                clean_word = word
                while clean_word and clean_word[-1] in '.,;:!?"()[]{}':
                    punctuation = clean_word[-1] + punctuation
                    clean_word = clean_word[:-1]
                
                if not clean_word:
                    sentence_words.append(word)
                    continue
                
                # Check if it's a known acronym
                if clean_word.upper() in acronyms:
                    sentence_words.append(clean_word.upper() + punctuation)
                # Check if it's a short all-caps acronym (2-5 letters, all uppercase)
                elif len(clean_word) >= 2 and len(clean_word) <= 5 and clean_word.isupper():
                    sentence_words.append(word)  # Keep short acronyms as is
                # First word of title or first word after colon - capitalize
                elif i == 0:
                    capitalized = clean_word[0].upper() + clean_word[1:].lower()
                    sentence_words.append(capitalized + punctuation)
                # All other words - lowercase
                else:
                    sentence_words.append(clean_word.lower() + punctuation)
            
            processed_parts.append(' '.join(sentence_words))
        
        return ': '.join(processed_parts)
    
    def format_citation(self) -> str:
        """
        Generate APA format citation based on citation type.

        Routes the citation to the appropriate type-specific formatter method
        (book, article, website, or report).

        Returns:
            str: Complete formatted APA citation with HTML markup

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
        Format authors list according to APA 7th edition rules.

        APA 7 author formatting rules:
        - 1 author: Last, F.
        - 2 authors: Last, F., & Last, F.
        - 3-20 authors: Last, F., Last, F., & Last, F.
        - 21+ authors: First 19 authors, ..., & Last author

        Args:
            authors (list): List of author names in "First Last" format

        Returns:
            str: Formatted authors string with proper punctuation and conjunctions

        Note:
            - Uses ampersand (&) before last author
            - Author names are normalized to "Last, F." format with initials
            - For 21+ authors, includes first 19, ellipsis, then last author
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
        """
        Convert author name to APA format with initials.

        Transforms author names from "First Last" format to APA style "Last, F." format
        where first/middle names are converted to initials.

        Args:
            author (str): Author name in "First Last" or "First Middle Last" format

        Returns:
            str: Author name in APA format "Last, F. M." with initials

        Examples:
            "John Smith" -> "Smith, J."
            "John Paul Jones" -> "Jones, J. P."
            "Smith" -> "Smith"

        Note:
            - All first and middle names become initials with periods
            - Last name always comes first in APA style
            - Single-name authors are returned as-is
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
        """
        Generate APA format book citation.

        APA book format: Authors. (Year). Title (edition). Publisher.

        Args:
            authors (str): Pre-formatted authors string

        Returns:
            str: Complete APA book citation

        Note:
            - Title is italicized and in sentence case
            - Edition is shown only if not first edition
            - Year defaults to "(n.d.)" if not provided
            - Final period added automatically
        """
        citation_parts = []
        
        if authors:
            # Remove trailing period from authors if present
            authors_clean = authors.rstrip('.')
            citation_parts.append(authors_clean)
        
        # Handle year or n.d.
        if self._citation.year:
            citation_parts.append(f"({self._citation.year})")
        else:
            citation_parts.append("(n.d.)")
        
        # Title with edition if available (using Sentence case)
        if self._citation.title:
            title_sentence_case = self._to_sentence_case(self._citation.title)
            title_part = f"<i>{title_sentence_case}</i>"
            if self._citation.edition and self._citation.edition != 1:
                # Normalize edition format for APA
                edition_text = self._normalize_edition(self._citation.edition)
                if edition_text:
                    title_part += f" ({edition_text})"
            citation_parts.append(title_part)
        
        if self._citation.publisher:
            citation_parts.append(self._citation.publisher)
        
        # Join with '. ' and add final period only if no DOI
        if citation_parts:
            result = ". ".join(citation_parts)
            if not result.endswith('.'):
                result += "."
            return result
        return ""
    
    def _format_article(self, authors: str) -> str:
        """
        Generate APA format article citation.

        APA article format: Authors. (Year). Article title. Journal Name, volume(issue), pages. DOI

        Args:
            authors (str): Pre-formatted authors string

        Returns:
            str: Complete APA article citation

        Note:
            - Article title is NOT italicized, in sentence case
            - Journal name and volume are italicized
            - Issue number in parentheses, not italicized
            - DOI URL is added without "Retrieved from" prefix
            - No final period if DOI is present
        """
        citation_parts = []
        
        if authors:
            # Remove trailing period from authors if present
            authors_clean = authors.rstrip('.')
            citation_parts.append(authors_clean)
        
        # Handle year or n.d.
        if self._citation.year:
            citation_parts.append(f"({self._citation.year})")
        else:
            citation_parts.append("(n.d.)")
            
        # Article titles are NOT in italics in APA (using Sentence case)
        if self._citation.title:
            title_sentence_case = self._to_sentence_case(self._citation.title)
            citation_parts.append(title_sentence_case)
        
        journal_part = ""
        if self._citation.journal:
            # Journal name should be in italics
            journal_part = f"<i>{self._citation.journal}</i>"
            if self._citation.volume:
                # Volume should also be in italics according to APA
                journal_part += f", <i>{self._citation.volume}</i>"
                if self._citation.issue:
                    # Issue number in regular text within parentheses
                    journal_part += f"({self._citation.issue})"
            if self._citation.pages:
                # Use en dash for page ranges in APA
                pages_formatted = self._citation.pages.replace('-', '–')
                journal_part += f", {pages_formatted}"
        
        if journal_part:
            citation_parts.append(journal_part)
        
        if self._citation.doi:
            # DOI should not have a trailing period since it's a URL
            citation_parts.append(f"https://doi.org/{self._citation.doi}")
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
        """
        Generate APA format website citation.

        APA website format: Authors. (Year). Page title. Website Name. URL

        Args:
            authors (str): Pre-formatted authors string

        Returns:
            str: Complete APA website citation

        Note:
            - Page title is in sentence case, not italicized
            - Website name (publisher) is italicized
            - Year defaults to "(n.d.)" if not provided
            - URL is added directly without "Retrieved from"
            - No final period after URL
        """
        citation_parts = []
        
        if authors:
            # Remove trailing period from authors if present
            authors_clean = authors.rstrip('.')
            citation_parts.append(authors_clean)
        
        # Handle year or n.d. for websites
        if self._citation.year:
            citation_parts.append(f"({self._citation.year})")
        else:
            citation_parts.append("(n.d.)")
        
        if self._citation.title:
            title_sentence_case = self._to_sentence_case(self._citation.title)
            citation_parts.append(title_sentence_case)
        
        # Add website name (publisher field) - Nombre del sitio
        if self._citation.publisher:
            citation_parts.append(f"<i>{self._citation.publisher}</i>")
        
        # For websites, we use the URL directly without "Retrieved from"
        if self._citation.url:
            citation_parts.append(self._citation.url)
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
        """
        Generate APA format report citation.

        APA report format: Authors. (Year). Title [Report]. Organization. URL

        Args:
            authors (str): Pre-formatted authors string

        Returns:
            str: Complete APA report citation

        Note:
            - Title is italicized with [Report] descriptor
            - Organization (publisher) is not italicized
            - Year defaults to "(n.d.)" if not provided
            - URL is added directly without "Retrieved from"
            - No final period after URL
        """
        citation_parts = []
        
        if authors:
            # Remove trailing period from authors if present
            authors_clean = authors.rstrip('.')
            citation_parts.append(authors_clean)
        
        # Handle year or n.d.
        if self._citation.year:
            citation_parts.append(f"({self._citation.year})")
        else:
            citation_parts.append("(n.d.)")
            
        if self._citation.title:
            # Title with report type specification (using Sentence case)
            title_sentence_case = self._to_sentence_case(self._citation.title)
            title_part = f"<i>{title_sentence_case}</i> [Report]"
            citation_parts.append(title_part)
        
        # Add institution/organization (publisher)
        if self._citation.publisher:
            citation_parts.append(self._citation.publisher)
        
        # Add URL if available (reports don't have DOI)
        if self._citation.url:
            citation_parts.append(self._citation.url)
            # No final period after URL
            return ". ".join(citation_parts)
        
        # Join with '. ' and add final period only if no URL
        if citation_parts:
            result = ". ".join(citation_parts)
            if not result.endswith('.'):
                result += "."
            return result
        return ""
