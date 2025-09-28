from sqlalchemy.orm import Session
from models.citation import Citation
from models.project_citation import ProjectCitation
import json

class CitationRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, project_id: int, type: str, title: str, authors: list[str], year: int, **kwargs) -> Citation:
        authors_json = json.dumps(authors)

        existing = (
            self.db.query(Citation)
            .filter(Citation.title == title, Citation.authors == authors_json, Citation.year == year)
            .first()
        )

        if existing:
            assoc = (
                self.db.query(ProjectCitation)
                .filter(ProjectCitation.project_id == project_id, ProjectCitation.citation_id == existing.id)
                .first()
            )
            if not assoc:
                new_assoc = ProjectCitation(project_id=project_id, citation_id=existing.id)
                self.db.add(new_assoc)
                self.db.commit()
            return existing

        citation = Citation(
            type=type,
            title=title,
            authors=authors_json,
            year=year,
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

        self.db.add(citation)
        self.db.commit()
        self.db.refresh(citation)

        assoc = ProjectCitation(project_id=project_id, citation_id=citation.id)
        self.db.add(assoc)
        self.db.commit()

        return citation
    
    def get_by_id(self, citation_id: int) -> Citation | None:
        return self.db.query(Citation).filter(Citation.id == citation_id).first()
    
    def delete(self, citation_id: int, project_id: int | None = None) -> bool:
        citation = self.get_by_id(citation_id)
        if not citation:
            return False

        associations = (
            self.db.query(ProjectCitation)
            .filter(ProjectCitation.citation_id == citation_id)
            .all()
        )

        if not associations:
            self.db.delete(citation)
            self.db.commit()
            return True

        if len(associations) > 1 and project_id:
            assoc = (
                self.db.query(ProjectCitation)
                .filter(ProjectCitation.citation_id == citation_id, ProjectCitation.project_id == project_id)
                .first()
            )
            if assoc:
                self.db.delete(assoc)
                self.db.commit()
            return True

        for assoc in associations:
            self.db.delete(assoc)
        self.db.delete(citation)
        self.db.commit()
        return True

    def update(self, citation_id: int, project_id: int, **kwargs) -> Citation | None:
        citation = self.get_by_id(citation_id)
        if not citation:
            return None

        if project_id is None:
            raise ValueError("project_id is required for citation updates")

        updated_data = {}
        for key, value in kwargs.items():
            if value is not None:
                if key == "authors" and isinstance(value, list):
                    updated_data[key] = json.dumps(value)
                else:
                    updated_data[key] = value

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
        
        final_data = {**current_data, **updated_data}

        existing_citation = (
            self.db.query(Citation)
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
                Citation.id != citation_id  
            )
            .first()
        )

        if existing_citation:
            existing_assoc = (
                self.db.query(ProjectCitation)
                .filter(ProjectCitation.project_id == project_id, ProjectCitation.citation_id == existing_citation.id)
                .first()
            )
            
            if not existing_assoc:
                new_assoc = ProjectCitation(project_id=project_id, citation_id=existing_citation.id)
                self.db.add(new_assoc)
            
            old_assoc = (
                self.db.query(ProjectCitation)
                .filter(ProjectCitation.project_id == project_id, ProjectCitation.citation_id == citation_id)
                .first()
            )
            if old_assoc:
                self.db.delete(old_assoc)
            
            remaining_assocs = (
                self.db.query(ProjectCitation)
                .filter(ProjectCitation.citation_id == citation_id)
                .count()
            )
            
            if remaining_assocs == 0:
                self.db.delete(citation)
            
            self.db.commit()
            return existing_citation

        current_associations = (
            self.db.query(ProjectCitation)
            .filter(ProjectCitation.citation_id == citation_id)
            .all()
        )

        if len(current_associations) == 1:
            for key, value in updated_data.items():
                if hasattr(citation, key):
                    setattr(citation, key, value)
            
            self.db.commit()
            self.db.refresh(citation)
            return citation
        
        else:
            new_citation = Citation(**final_data)
            self.db.add(new_citation)
            self.db.flush() 
            self.db.refresh(new_citation)
            
            old_assoc = (
                self.db.query(ProjectCitation)
                .filter(ProjectCitation.project_id == project_id,ProjectCitation.citation_id == citation_id)
                .first()
            )
            if old_assoc:
                self.db.delete(old_assoc)
            
            new_assoc = ProjectCitation(project_id=project_id, citation_id=new_citation.id)
            self.db.add(new_assoc)
            
            self.db.commit()
            self.db.refresh(new_citation)
            return new_citation