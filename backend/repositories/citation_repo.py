from sqlalchemy.orm import Session
from models.citation import Citation
from models.project_citation import ProjectCitation
from config.citation_config import CitationConfig
import json

class CitationRepository:
    """
    Repository class for managing citation data operations.
    
    This class handles all database interactions for citations and their associations
    with projects. It provides CRUD operations while ensuring data integrity,
    avoiding duplicates, and properly managing many-to-many relationships between
    citations and projects.
    
    Attributes:
        db (Session): SQLAlchemy database session for executing queries
    """
    
    def __init__(self, db: Session):
        """
        Initialize the citation repository with a database session.
        
        Args:
            db (Session): SQLAlchemy database session for database operations
        """
        self._db = db

    def create(self, project_id: int, **kwargs) -> Citation:
        """
        Create a new citation or associate an existing identical citation with a project.
        
        Args:
            project_id (int): ID of the project to associate the citation with
            **kwargs: Citation data including type, title, authors, year, etc.
                
        Returns:
            Citation: The created or existing citation object
            
        Note:
            - Authors are stored as JSON in the database
            - All validation is assumed to be done before calling this method
        """
        # Convert authors list to JSON for database storage
        authors_json = json.dumps(kwargs.get("authors"))

        # Check if an identical citation already exists to avoid duplicates
        # Compare all relevant fields to ensure exact match
        existing = (
            self._db.query(Citation)
            .filter(
                Citation.type == kwargs.get("type"),
                Citation.title == kwargs.get("title"), 
                Citation.authors == authors_json, 
                Citation.year == kwargs.get("year"),
                Citation.publisher == kwargs.get("publisher"),
                Citation.journal == kwargs.get("journal"),
                Citation.volume == kwargs.get("volume"),
                Citation.issue == kwargs.get("issue"),
                Citation.pages == kwargs.get("pages"),
                Citation.doi == kwargs.get("doi"),
                Citation.url == kwargs.get("url"),
                Citation.access_date == kwargs.get("access_date"),
                Citation.place == kwargs.get("place"),
                Citation.edition == kwargs.get("edition")
            )
            .first()
        )

        if existing:
            # If identical citation exists, just create project association if needed
            assoc = (
                self._db.query(ProjectCitation)
                .filter(ProjectCitation.project_id == project_id, ProjectCitation.citation_id == existing.id)
                .first()
            )
            if not assoc:
                # Create new project-citation association
                new_assoc = ProjectCitation(project_id=project_id, citation_id=existing.id)
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
    
    def get_by_id(self, citation_id: int) -> Citation | None:
        """
        Retrieve a citation by its unique identifier.
        
        Args:
            citation_id (int): Unique identifier of the citation
            
        Returns:
            Citation | None: The citation object if found, None otherwise
        """
        return self._db.query(Citation).filter(Citation.id == citation_id).first()

    def delete(self, citation_id: int, project_id: int | None = None) -> bool:
        """
        Delete a citation or remove its association with a project.
        
        This method handles different deletion scenarios:
        1. If no project associations exist, delete the citation entirely
        2. If multiple associations exist and project_id is provided, remove only that association
        3. If citation has associations but none match project_id, remove all associations and citation
        
        Args:
            citation_id (int): ID of the citation to delete
            project_id (int | None): ID of the project for selective association removal
            
        Returns:
            bool: True if deletion was successful, False if citation not found
        """
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

        # If it has exactly one association, delete the association and then the citation
        if len(associations) == 1:
            assoc = associations[0]
            self._db.delete(assoc)
            self._db.delete(citation)
            self._db.commit()
            return True

        # If multiple associations exist, remove only the specified project association
        if len(associations) > 1:
            assoc = (
                self._db.query(ProjectCitation)
                .filter(ProjectCitation.citation_id == citation_id, ProjectCitation.project_id == project_id)
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

    def update(self, citation_id: int, project_id: int, **kwargs) -> Citation | None:
        """
        Update an existing citation with new data, handling duplicates and shared citations.
        
        Args:
            citation_id (int): ID of the citation to update
            project_id (int): ID of the associated project (required for update tracking)
            **kwargs: Fields to update, can include any citation field
            
        Returns:
            Citation | None: The updated citation object or None if citation not found
            
        Raises:
            ValueError: If project_id is not provided
            
        Note:
            - If citation is shared by multiple projects and changes would affect others,
              a new citation is created for this project
        """
        citation = self.get_by_id(citation_id)
        if not citation:
            return None

        # Prepare update data with proper JSON encoding for authors
        updated_data = {}
        for key, value in kwargs.items():
            if value is not None:
                if key == "authors" and isinstance(value, list):
                    # Convert authors list to JSON string for database storage
                    updated_data[key] = json.dumps(value)
                else:
                    updated_data[key] = value

        # Get current citation data for comparison and merging
        current_data = {
            'type': citation.type,
            'title': citation.title,
            'authors': citation.authors,
            'year': citation.year,
            'publisher': citation.publisher,
            'journal': citation.journal,
            'volume': citation.volume,
            'issue': citation.issue,
            'pages': citation.pages,
            'doi': citation.doi,
            'url': citation.url,
            'access_date': citation.access_date,
            'place': citation.place,
            'edition': citation.edition,
        }
        
        # Merge current data with updates, prioritizing new data
        final_data = {**current_data}
        for key, value in updated_data.items():
            final_data[key] = value  

        # Filter fields by citation type - set to None all fields not associated with the type
        citation_type = final_data.get('type', citation.type)
        config = CitationConfig()
        if config.is_valid_type(citation_type):
            allowed_fields = config.get_required_fields(citation_type)
            for field in config.get_all_fields():
                if field not in allowed_fields:
                    final_data[field] = None

        # Check if an identical citation already exists to avoid duplicates
        existing_citation = (
            self._db.query(Citation)
            .filter(
                Citation.title == final_data['title'],
                Citation.authors == final_data['authors'],
                Citation.year == final_data['year'],
                Citation.type == final_data['type'],
                Citation.publisher == final_data['publisher'],
                Citation.journal == final_data['journal'],
                Citation.volume == final_data['volume'],
                Citation.issue == final_data['issue'],
                Citation.pages == final_data['pages'],
                Citation.doi == final_data['doi'],
                Citation.url == final_data['url'],
                Citation.access_date == final_data['access_date'],
                Citation.place == final_data['place'],
                Citation.edition == final_data['edition'],
                Citation.id != citation_id  # Exclude the current citation from the search
            )
            .first()
        )

        if existing_citation:
            # If identical citation exists, switch project association to existing citation
            existing_assoc = (
                self._db.query(ProjectCitation)
                .filter(ProjectCitation.project_id == project_id, ProjectCitation.citation_id == existing_citation.id)
                .first()
            )
            
            # Create association with existing citation if it doesn't exist
            if not existing_assoc:
                new_assoc = ProjectCitation(project_id=project_id, citation_id=existing_citation.id)
                self._db.add(new_assoc)
            
            # Remove association with the old citation
            old_assoc = (
                self._db.query(ProjectCitation)
                .filter(ProjectCitation.project_id == project_id, ProjectCitation.citation_id == citation_id)
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
            # Safe to modify the citation directly since no other projects use it
            # Use final_data which has already been filtered by citation type
            for key, value in final_data.items():
                if hasattr(citation, key):
                    setattr(citation, key, value)
            
            self._db.commit()
            self._db.refresh(citation)
            return citation
        
        else:
            # If multiple projects use this citation, create a new one for this project
            # This prevents changes from affecting other projects' citations
            new_citation = Citation(**final_data)
            self._db.add(new_citation)
            self._db.flush()  # Get the new citation ID without committing
            self._db.refresh(new_citation)
            
            # Remove old association and create new one
            old_assoc = (
                self._db.query(ProjectCitation)
                .filter(ProjectCitation.project_id == project_id, ProjectCitation.citation_id == citation_id)
                .first()
            )
            if old_assoc:
                self._db.delete(old_assoc)
            
            # Associate the new citation with the project
            new_assoc = ProjectCitation(project_id=project_id, citation_id=new_citation.id)
            self._db.add(new_assoc)
            
            self._db.commit()
            self._db.refresh(new_citation)
            return new_citation