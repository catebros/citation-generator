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
            .filter(
                Citation.title == title,
                Citation.authors == authors_json,
                Citation.year == year,
            )
            .first()
        )

        if existing:
            assoc = (
                self.db.query(ProjectCitation)
                .filter(
                    ProjectCitation.project_id == project_id,
                    ProjectCitation.citation_id == existing.id,
                )
                .first()
            )
            if not assoc:
                new_assoc = ProjectCitation(
                    project_id=project_id,
                    citation_id=existing.id
                )
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
    
    def get_all_by_project(self, project_id: int) -> list[Citation]:
        return (
            self.db.query(Citation)
            .join(ProjectCitation, Citation.id == ProjectCitation.citation_id)
            .filter(ProjectCitation.project_id == project_id)
            .order_by(Citation.year.desc())
            .all()
        )
    
    def delete(self, citation_id: int) -> bool:
        citation = self.get_by_id(citation_id)
        if not citation:
            return False

        self.db.delete(citation)
        self.db.commit()
        return True

    def update(self, citation_id: int, **kwargs) -> Citation | None:
        citation = self.get_by_id(citation_id)
        if not citation:
            return None

        for key, value in kwargs.items():
            if value is None:
                continue

            if key == "authors" and isinstance(value, list):
                value = json.dumps(value)

            if hasattr(citation, key):
                setattr(citation, key, value)

        self.db.commit()
        self.db.refresh(citation)
        return citation  