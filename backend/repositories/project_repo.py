from sqlalchemy.orm import Session
from models.project import Project
from models.citation import Citation
from models.project_citation import ProjectCitation

class ProjectRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, name: str) -> Project:
        project = Project(name=name)
        self.db.add(project)
        self.db.commit()
        self.db.refresh(project)
        return project
    
    def get_by_id(self, project_id: int)-> Project | None:
        return self.db.query(Project).filter(Project.id == project_id).first()
    
    def get_all(self)-> list[Project]: 
        return self.db.query(Project).all()
    
    def update(self, project_id: int, **kwargs)-> Project | None:
        project = self.get_by_id(project_id)

        if not project:
            return None
        
        for key, value in kwargs.items():
            if value is None:
                continue

            if hasattr(project, key):
                setattr(project, key, value)

                
        self.db.commit()
        self.db.refresh(project)
        return project         

    def delete(self, project_id: int) -> bool:
        project = self.get_by_id(project_id)

        if not project:
            return False

        project_associations = (
            self.db.query(ProjectCitation)
            .filter(ProjectCitation.project_id == project_id)
            .all()
        )
        
        for assoc in project_associations:
            citation_id = assoc.citation_id
            
            self.db.delete(assoc)
            
            remaining_assocs = (
                self.db.query(ProjectCitation)
                .filter(
                    ProjectCitation.citation_id == citation_id,
                    ProjectCitation.project_id != project_id 
                )
                .count()
            )
            
            if remaining_assocs == 0:
                citation = (
                    self.db.query(Citation)
                    .filter(Citation.id == citation_id)
                    .first()
                )
                if citation:
                    self.db.delete(citation)
        
        self.db.delete(project)
        self.db.commit()
        return True