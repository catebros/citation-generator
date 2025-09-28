from repositories.citation_repo import CitationRepository
from repositories.project_repo import ProjectRepository
from fastapi import HTTPException

class ProjectService:
    def __init__(self, db):
        self.project_repo = ProjectRepository(db)
        self.citation_repo = CitationRepository(db)

    def create_project(self, data: dict):
        name = data.get("name")
        if not name or name.strip() == "":
            raise HTTPException(status_code=400, detail="Project name cannot be empty")

        if self.project_repo.get_by_name(name):
            raise HTTPException(status_code=400, detail="Project with this name already exists")

        return self.project_repo.create(name=name)

    def get_project(self, project_id: int):
        project = self.project_repo.get_by_id(project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        return project

    def get_all_projects(self):
        return self.project_repo.get_all()

    def update_project(self, project_id: int, data: dict):
        project = self.project_repo.update(project_id, **data)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        return project

    def delete_project(self, project_id: int):
        success = self.project_repo.delete(project_id)
        if not success:
            raise HTTPException(status_code=404, detail="Project not found")
        return {"message": "Project deleted"}

    def get_all_citations_by_project(self, project_id: int):
        project = self.project_repo.get_by_id(project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        return self.citation_repo.get_all_by_project(project_id)

    def generate_bibliography_by_project():
        ...    