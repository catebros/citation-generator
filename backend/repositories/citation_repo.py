from sqlalchemy.orm import Session
from models.citation import Citation
import json

class CitationRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, type: str, title: str, authors: list[str], year: int, **kwargs) -> Citation:
        citation = Citation(
            type=type,
            title=title,
            authors=json.dumps(authors),
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
        return citation
