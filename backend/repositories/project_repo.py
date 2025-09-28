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
        ...