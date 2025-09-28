from repositories.citation_repo import CitationRepository
from repositories.project_repo import ProjectRepository
from fastapi import HTTPException

class CitationService:
    def __init__(self, db):
        self.citation_repo = CitationRepository(db)
        self.project_repo = ProjectRepository(db)

    def create_citation(self, project_id:int, data:dict):
        project = self.project_repo.get_by_id(project_id)

        if not project:
            raise HTTPException(status_code=404, detail="Project not found")   
        
        required_fields = ["type", "title", "authors", "year"]
        missing = [f for f in required_fields if not data.get(f)]
        if missing:
            raise HTTPException(status_code=400, detail=f"Missing required fields: {', '.join(missing)}")

        if not isinstance(data["authors"], list):
            raise HTTPException(status_code=400, detail="Authors must be a list")
        
        return self.citation_repo.create(project_id=project_id, **data)
    
    def get_citation(self, citation_id: int):
        citation = self.citation_repo.get_by_id(citation_id)
        if not citation:
            raise HTTPException(status_code=404, detail="Citation not found")
        return citation

    def update_citation(self, citation_id: int, project_id: int, data: dict):
        citation = self.citation_repo.get_by_id(citation_id)
        if not citation:
            raise HTTPException(status_code=404, detail="Citation not found")

        updated = self.citation_repo.update(citation_id=citation_id, project_id=project_id, **data)
        if not updated:
            raise HTTPException(status_code=400, detail="Update failed")

        return updated

    def delete_citation(self, citation_id: int, project_id: int | None = None):
        success = self.citation_repo.delete(citation_id=citation_id, project_id=project_id)
        if not success:
            raise HTTPException(status_code=404, detail="Citation not found")
        return {"message": "Citation deleted"}