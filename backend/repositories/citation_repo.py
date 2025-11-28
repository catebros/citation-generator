# backend/repositories/citation_repo.py
"""
Citation repository for CRUD operations with duplicate detection.
"""
import json
from typing import Any, Dict, List, Optional

from config.citation_config import CitationFieldsConfig
from models.citation import Citation
from models.project_citation import ProjectCitation
from sqlalchemy import inspect
from sqlalchemy.orm import Session


def _get_citation_valid_fields() -> List[str]:
    """Get valid citation fields from model, excluding id and created_at."""
    mapper = inspect(Citation)
    excluded_fields = {"id", "created_at"}
    return [
        column.key for column in mapper.columns if column.key not in excluded_fields
    ]


CITATION_VALID_FIELDS = _get_citation_valid_fields()


class CitationRepository:
    """Handle citation CRUD, duplicate detection, and project-citation associations."""

    def __init__(self, db: Session) -> None:
        """Initialize repository with database session."""
        self._db = db

    def create(self, project_id: int, **kwargs) -> Citation:
        """Create citation or reuse existing identical citation."""
        # Handle authors - list or already-serialized JSON string
        authors_value = kwargs.get("authors")
        if isinstance(authors_value, list):
            authors_json = json.dumps(authors_value)
        else:
            authors_json = authors_value  # Already serialized

        # Check if an identical citation already exists to avoid duplicates
        # Compare all relevant fields to ensure exact match
        year_val = kwargs.get("year")
        publisher_val = kwargs.get("publisher")
        journal_val = kwargs.get("journal")
        volume_val = kwargs.get("volume")
        issue_val = kwargs.get("issue")
        pages_val = kwargs.get("pages")
        doi_val = kwargs.get("doi")
        url_val = kwargs.get("url")
        access_date_val = kwargs.get("access_date")
        place_val = kwargs.get("place")
        edition_val = kwargs.get("edition")
        
        existing = (
            self._db.query(Citation)
            .filter(
                Citation.type == kwargs.get("type"),
                Citation.title == kwargs.get("title"),
                Citation.authors == authors_json,
                Citation.year.is_(year_val) if year_val is None else (Citation.year == year_val),
                (Citation.publisher.is_(None) if publisher_val is None else (Citation.publisher == publisher_val)),
                (Citation.journal.is_(None) if journal_val is None else (Citation.journal == journal_val)),
                (Citation.volume.is_(None) if volume_val is None else (Citation.volume == volume_val)),
                (Citation.issue.is_(None) if issue_val is None else (Citation.issue == issue_val)),
                (Citation.pages.is_(None) if pages_val is None else (Citation.pages == pages_val)),
                (Citation.doi.is_(None) if doi_val is None else (Citation.doi == doi_val)),
                (Citation.url.is_(None) if url_val is None else (Citation.url == url_val)),
                (Citation.access_date.is_(None) if access_date_val is None else (Citation.access_date == access_date_val)),
                (Citation.place.is_(None) if place_val is None else (Citation.place == place_val)),
                (Citation.edition.is_(None) if edition_val is None else (Citation.edition == edition_val)),
            )
            .first()
        )

        if existing:
            # If identical citation exists, just create project association if needed
            assoc = (
                self._db.query(ProjectCitation)
                .filter(
                    ProjectCitation.project_id == project_id,
                    ProjectCitation.citation_id == existing.id,
                )
                .first()
            )
            if not assoc:
                # Create new project-citation association
                new_assoc = ProjectCitation(
                    project_id=project_id, citation_id=existing.id
                )
                self._db.add(new_assoc)
                self._db.commit()
            return existing

        # Create new citation with all provided fields
        citation = Citation(
            type=kwargs.get("type"),
            title=kwargs.get("title"),
            authors=authors_json,
            year=kwargs.get("year"),
            publisher=kwargs.get("publisher"),
            journal=kwargs.get("journal"),
            volume=kwargs.get("volume"),
            issue=kwargs.get("issue"),
            pages=kwargs.get("pages"),
            doi=kwargs.get("doi"),
            url=kwargs.get("url"),
            access_date=kwargs.get("access_date"),
            place=kwargs.get("place"),
            edition=kwargs.get("edition"),
        )

        # Save citation to database and get generated ID
        self._db.add(citation)
        self._db.commit()
        self._db.refresh(citation)

        # Create project-citation association
        assoc = ProjectCitation(project_id=project_id, citation_id=citation.id)
        self._db.add(assoc)
        self._db.commit()

        return citation

    def merge_citation_data(
        self, current_citation: Citation, update_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Merge citation with update data and filter by type."""
        # Prepare update data with proper JSON encoding for authors
        processed_updates = {}
        for key, value in update_data.items():
            if key == "authors" and isinstance(value, list):
                # Convert authors list to JSON string for database storage
                processed_updates[key] = json.dumps(value)
            else:
                processed_updates[key] = value

        # Get current citation data for comparison and merging
        current_data = {
            "type": current_citation.type,
            "title": current_citation.title,
            "authors": current_citation.authors,
            "year": current_citation.year,
            "publisher": current_citation.publisher,
            "journal": current_citation.journal,
            "volume": current_citation.volume,
            "issue": current_citation.issue,
            "pages": current_citation.pages,
            "doi": current_citation.doi,
            "url": current_citation.url,
            "access_date": current_citation.access_date,
            "place": current_citation.place,
            "edition": current_citation.edition,
        }

        # Merge current data with updates, prioritizing new data
        final_data = {**current_data}
        for key, value in processed_updates.items():
            final_data[key] = value

        # Filter fields by citation type
        citation_type = final_data.get("type", current_citation.type)
        config = CitationFieldsConfig()
        if config.is_valid_type(citation_type):
            allowed_fields = config.get_required_fields(citation_type)
            for field in CITATION_VALID_FIELDS:
                if field not in allowed_fields:
                    final_data[field] = None

        return final_data

    def find_duplicate_citation_in_project(
        self, project_id: int, data: Dict[str, Any]
    ) -> Optional[Citation]:
        """Find identical citation in project based on type-specific required fields."""
        # Convert authors to JSON for comparison
        authors_value = data.get("authors")
        if isinstance(authors_value, list):
            authors_json = json.dumps(authors_value)
        else:
            authors_json = authors_value  # Already serialized

        # Build base query
        query = (
            self._db.query(Citation)
            .join(ProjectCitation, Citation.id == ProjectCitation.citation_id)
            .filter(ProjectCitation.project_id == project_id)
        )

        # Get citation type to determine which fields to check
        citation_type = data.get("type", "").lower()

        # Always check these core fields for all types
        query = query.filter(Citation.type.ilike(citation_type))
        query = query.filter(Citation.title.ilike(data.get("title", "")))
        query = query.filter(Citation.authors.ilike(authors_json))
        
        # Handle year comparison - use is_() for None values
        year_val = data.get("year")
        if year_val is None:
            query = query.filter(Citation.year.is_(None))
        else:
            query = query.filter(Citation.year == year_val)

        # Type-specific field comparisons based on required fields
        if citation_type == "book":
            # For books: check publisher, place, edition
            publisher_val = data.get("publisher", "")
            if publisher_val:
                query = query.filter(Citation.publisher.ilike(publisher_val))
            else:
                query = query.filter(Citation.publisher.is_(None))
                
            place_val = data.get("place", "")
            if place_val:
                query = query.filter(Citation.place.ilike(place_val))
            else:
                query = query.filter(Citation.place.is_(None))
                
            edition_val = data.get("edition")
            if edition_val is not None:
                query = query.filter(Citation.edition == edition_val)
            else:
                query = query.filter(Citation.edition.is_(None))

        elif citation_type == "article":
            # For articles: check journal, volume, pages, issue, doi
            journal_val = data.get("journal", "")
            if journal_val:
                query = query.filter(Citation.journal.ilike(journal_val))
            else:
                query = query.filter(Citation.journal.is_(None))
                
            # Handle volume comparison - use is_() for None values
            volume_val = data.get("volume")
            if volume_val is None:
                query = query.filter(Citation.volume.is_(None))
            else:
                query = query.filter(Citation.volume == volume_val)
                
            pages_val = data.get("pages", "")
            if pages_val:
                query = query.filter(Citation.pages.ilike(pages_val))
            else:
                query = query.filter(Citation.pages.is_(None))
                
            issue_val = data.get("issue")
            if issue_val:
                query = query.filter(Citation.issue.ilike(issue_val))
            else:
                query = query.filter(Citation.issue.is_(None))
                
            doi_val = data.get("doi")
            if doi_val:
                query = query.filter(Citation.doi.ilike(doi_val))
            else:
                query = query.filter(Citation.doi.is_(None))

        elif citation_type == "website":
            # For websites: check publisher, url, access_date
            publisher_val = data.get("publisher", "")
            if publisher_val:
                query = query.filter(Citation.publisher.ilike(publisher_val))
            else:
                query = query.filter(Citation.publisher.is_(None))
                
            url_val = data.get("url", "")
            if url_val:
                query = query.filter(Citation.url.ilike(url_val))
            else:
                query = query.filter(Citation.url.is_(None))
                
            access_date_val = data.get("access_date")
            if access_date_val:
                query = query.filter(Citation.access_date == access_date_val)
            else:
                query = query.filter(Citation.access_date.is_(None))

        elif citation_type == "report":
            # For reports: check publisher, place, url
            publisher_val = data.get("publisher", "")
            if publisher_val:
                query = query.filter(Citation.publisher.ilike(publisher_val))
            else:
                query = query.filter(Citation.publisher.is_(None))
                
            place_val = data.get("place", "")
            if place_val:
                query = query.filter(Citation.place.ilike(place_val))
            else:
                query = query.filter(Citation.place.is_(None))
                
            url_val = data.get("url")
            if url_val:
                query = query.filter(Citation.url.ilike(url_val))
            else:
                query = query.filter(Citation.url.is_(None))

        return query.first()

    def get_by_id(self, citation_id: int) -> Optional[Citation]:
        """Retrieve citation by unique identifier."""
        return self._db.query(Citation).filter(Citation.id == citation_id).first()

    def delete(self, citation_id: int, project_id: Optional[int] = None) -> bool:
        """Delete citation or remove project association."""
        citation = self.get_by_id(citation_id)
        if not citation:
            return False

        # Get all project associations for this citation
        associations = (
            self._db.query(ProjectCitation)
            .filter(ProjectCitation.citation_id == citation_id)
            .all()
        )

        # If no associations exist or project_id is None, delete the citation directly
        if not associations or project_id is None:
            # Delete any remaining associations first
            for assoc in associations:
                self._db.delete(assoc)
            self._db.delete(citation)
            self._db.commit()
            return True

        # If exactly one association, delete both association and citation
        if len(associations) == 1:
            assoc = associations[0]
            self._db.delete(assoc)
            self._db.delete(citation)
            self._db.commit()
            return True

        # If multiple associations, remove only specified project
        if len(associations) > 1:
            assoc = (
                self._db.query(ProjectCitation)
                .filter(
                    ProjectCitation.citation_id == citation_id,
                    ProjectCitation.project_id == project_id,
                )
                .first()
            )
            if assoc:
                self._db.delete(assoc)
                self._db.commit()
            return True

        # Remove all associations and then delete the citation
        for assoc in associations:
            self._db.delete(assoc)
        self._db.delete(citation)
        self._db.commit()
        return True

    def update(self, citation_id: int, project_id: int, **kwargs) -> Optional[Citation]:
        """Update citation, handling duplicates and shared cases."""
        citation = self.get_by_id(citation_id)
        if not citation:
            return None

        # Use the helper function to merge and process the data
        final_data = self.merge_citation_data(citation, kwargs)

        # Check if an identical citation already exists to avoid duplicates
        existing_citation = (
            self._db.query(Citation)
            .filter(
                Citation.title == final_data["title"],
                Citation.authors == final_data["authors"],
                Citation.year == final_data["year"],
                Citation.type == final_data["type"],
                Citation.publisher == final_data["publisher"],
                Citation.journal == final_data["journal"],
                Citation.volume == final_data["volume"],
                Citation.issue == final_data["issue"],
                Citation.pages == final_data["pages"],
                Citation.doi == final_data["doi"],
                Citation.url == final_data["url"],
                Citation.access_date == final_data["access_date"],
                Citation.place == final_data["place"],
                Citation.edition == final_data["edition"],
                Citation.id != citation_id,  # Exclude current citation
            )
            .first()
        )

        if existing_citation:
            # If identical citation exists, switch project association
            existing_assoc = (
                self._db.query(ProjectCitation)
                .filter(
                    ProjectCitation.project_id == project_id,
                    ProjectCitation.citation_id == existing_citation.id,
                )
                .first()
            )

            # Create association with existing citation if it doesn't exist
            if not existing_assoc:
                new_assoc = ProjectCitation(
                    project_id=project_id, citation_id=existing_citation.id
                )
                self._db.add(new_assoc)

            # Remove association with the old citation
            old_assoc = (
                self._db.query(ProjectCitation)
                .filter(
                    ProjectCitation.project_id == project_id,
                    ProjectCitation.citation_id == citation_id,
                )
                .first()
            )
            if old_assoc:
                self._db.delete(old_assoc)

            # Delete the old citation if no other projects are using it
            remaining_assocs = (
                self._db.query(ProjectCitation)
                .filter(ProjectCitation.citation_id == citation_id)
                .count()
            )

            if remaining_assocs == 0:
                self._db.delete(citation)

            self._db.commit()
            return existing_citation

        # Get current project associations for this citation
        current_associations = (
            self._db.query(ProjectCitation)
            .filter(ProjectCitation.citation_id == citation_id)
            .all()
        )

        # If only one project uses this citation, update it in place
        if len(current_associations) == 1:
            # Safe to modify directly since no other projects use it
            for key, value in final_data.items():
                if hasattr(citation, key):
                    setattr(citation, key, value)

            self._db.commit()
            self._db.refresh(citation)
            return citation

        else:
            # If multiple projects use this citation, create new one
            new_citation = Citation(**final_data)
            self._db.add(new_citation)
            self._db.flush()  # Get the new citation ID without committing
            self._db.refresh(new_citation)

            # Remove old association and create new one
            old_assoc = (
                self._db.query(ProjectCitation)
                .filter(
                    ProjectCitation.project_id == project_id,
                    ProjectCitation.citation_id == citation_id,
                )
                .first()
            )
            if old_assoc:
                self._db.delete(old_assoc)

            # Associate the new citation with the project
            new_assoc = ProjectCitation(
                project_id=project_id, citation_id=new_citation.id
            )
            self._db.add(new_assoc)

            self._db.commit()
            self._db.refresh(new_citation)
            return new_citation
