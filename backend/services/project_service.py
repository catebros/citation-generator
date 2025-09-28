from repositories.citation_repo import CitationRepository
from repositories.project_repo import ProjectRepository
from fastapi import HTTPException

class ProjectService:
    def __init__(self, db):
        self.project_repo = ProjectRepository(db)

    def create_project(self, project_id:int, data:dict):
        ...
        
    def get_project():
        ...

    def get_all_projects():
        ...    

    def update_project():
        ...

    def delete_project():
        ...    

    def get_all_citations_by_project():
        ...    

    def generate_bibliography_by_project():
        ...    