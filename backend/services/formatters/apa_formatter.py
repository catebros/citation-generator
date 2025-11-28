# backend/services/formatters/apa_formatter.py
from typing import TYPE_CHECKING, List

from .base_citation_formatter import BaseCitationFormatter

if TYPE_CHECKING:
    from models.citation import Citation


class APAFormatter(BaseCitationFormatter):
    """Format citations according to APA 7th edition guidelines."""

    def __init__(self, citation: "Citation"):
        """Initialize APA formatter with citation data."""
        super().__init__(citation)

    def _to_sentence_case(self, title: str) -> str:
        """Convert title to APA sentence case preserving acronyms and proper nouns."""
        if not title:
            return ""

        # Known acronyms and abbreviations that should stay uppercase
        acronyms = {
            # Technology & Computing
            "AI",
            "API",
            "AR",
            "AWS",
            "CDN",
            "CLI",
            "CPU",
            "CSS",
            "CSV",
            "DNA",
            "DOS",
            "DVD",
            "FAQ",
            "FTP",
            "GIF",
            "GPS",
            "GPU",
            "GUI",
            "HTML",
            "HTTP",
            "HTTPS",
            "IDE",
            "IoT",
            "IP",
            "IT",
            "JPEG",
            "JPG",
            "JS",
            "JSON",
            "LAN",
            "LED",
            "ML",
            "NLP",
            "OS",
            "PC",
            "PDF",
            "PHP",
            "PNG",
            "RAM",
            "REST",
            "RGB",
            "ROM",
            "SaaS",
            "SDK",
            "SEO",
            "SQL",
            "SSH",
            "SSL",
            "TCP",
            "TLS",
            "UI",
            "URL",
            "USB",
            "UX",
            "VPN",
            "VR",
            "WAN",
            "WiFi",
            "WWW",
            "XML",
            "YAML",
            "ZIP",
            # Organizations & Institutions
            "CIA",
            "FBI",
            "FDA",
            "NATO",
            "NASA",
            "NOAA",
            "UNESCO",
            "UNICEF",
            "UN",
            "WHO",
            "EU",
            "EPA",
            "FCC",
            "CDC",
            "MIT",
            "UCLA",
            "CUNY",
            "NYU",
            "USC",
            "IEEE",
            # Business & Finance
            "CEO",
            "CFO",
            "CTO",
            "COO",
            "CPA",
            "LLC",
            "IPO",
            "GDP",
            "SEC",
            "IRS",
            "NYSE",
            "ATM",
            "ETF",
            "ROI",
            "KPI",
            "B2B",
            "B2C",
            "HR",
            "PR",
            "RFP",
            "SLA",
            # Science & Medicine
            "DNA",
            "RNA",
            "HIV",
            "AIDS",
            "MRI",
            "CT",
            "EEG",
            "ECG",
            "PCR",
            "STEM",
            "ADHD",
            "OCD",
            "PTSD",
            "BMI",
            "FDA",
            "CDC",
            "WHO",
            # Education & Testing
            "ACT",
            "SAT",
            "GPA",
            "GRE",
            "GMAT",
            "TOEFL",
            "IELTS",
            "IQ",
            "EQ",
            "AP",
            "IB",
            "PhD",
            "MBA",
            "BA",
            "BS",
            "MA",
            "MS",
            "MD",
            "JD",
            "EdD",
            "DDS",
            # Media & Communication
            "TV",
            "DVD",
            "CD",
            "FM",
            "AM",
            "PM",
            "BBC",
            "CNN",
            "ESPN",
            "HBO",
            "NBC",
            "CBS",
            "ABC",
            "NPR",
            "PBS",
            "RSS",
            "SMS",
            "MMS",
            "DM",
            # Geography & Countries
            "USA",
            "UK",
            "UAE",
            "EU",
            "USSR",
            "NYC",
            "LA",
            "DC",
            "SF",
            # Military & Defense
            "FBI",
            "CIA",
            "NSA",
            "DOD",
            "RAF",
            "USAF",
            "NATO",
            "ICBM",
            # Miscellaneous
            "FAQ",
            "DIY",
            "ASAP",
            "FYI",
            "RSVP",
            "TBD",
            "TBA",
            "ETA",
            "OK",
            "AWOL",
            "PS",
            "vs",
            "VS",
            "aka",
            "AKA",
            "etc",
            "ETC",
            "ie",
            "IE",
            "eg",
            "EG",
        }

        # Split by colon to handle subtitles
        parts = title.split(":")
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
                elif (
                    len(clean_word) >= 2
                    and len(clean_word) <= 5
                    and clean_word.isupper()
                ):
                    sentence_words.append(word)  # Keep short acronyms as is
                # First word of title or first word after colon - capitalize
                elif i == 0:
                    capitalized = clean_word[0].upper() + clean_word[1:].lower()
                    sentence_words.append(capitalized + punctuation)
                # All other words - lowercase
                else:
                    sentence_words.append(clean_word.lower() + punctuation)

            processed_parts.append(" ".join(sentence_words))

        return ": ".join(processed_parts)

    def format_citation(self) -> str:
        """Route citation to type-specific formatter based on citation type."""
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
        """Format authors per APA 7th edition with ampersand before last author."""
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
        """Convert author to APA format with initials (Last, F. M.)."""
        author = author.strip()
        if not author:
            return ""

        # format "First Last", convert to "Last, F."
        parts = author.split()
        if len(parts) >= 2:
            first_names = parts[:-1]
            last_name = parts[-1]
            initials = ". ".join([name[0].upper() for name in first_names]) + "."
            return f"{last_name}, {initials}"

        # Single name, return as is
        return author

    def _format_book(self, authors: str) -> str:
        """Generate APA book citation with italicized title in sentence case."""
        citation_parts = []

        if authors:
            # Remove trailing period from authors if present
            authors_clean = authors.rstrip(".")
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
            if not result.endswith("."):
                result += "."
            return result
        return ""

    def _format_article(self, authors: str) -> str:
        """Generate APA article citation with italicized journal name and DOI."""
        citation_parts = []

        if authors:
            # Remove trailing period from authors if present
            authors_clean = authors.rstrip(".")
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
                pages_formatted = self._citation.pages.replace("-", "–")
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
            if not result.endswith("."):
                result += "."
            return result
        return ""

    def _format_website(self, authors: str) -> str:
        """Generate APA website citation with italicized publisher name and URL."""
        citation_parts = []

        if authors:
            # Remove trailing period from authors if present
            authors_clean = authors.rstrip(".")
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
            if not result.endswith("."):
                result += "."
            return result
        return ""

    def _format_report(self, authors: str) -> str:
        """Generate APA report citation with [Report] descriptor and italicized title."""
        citation_parts = []

        if authors:
            # Remove trailing period from authors if present
            authors_clean = authors.rstrip(".")
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
            if not result.endswith("."):
                result += "."
            return result
        return ""
