from sqlalchemy.orm import Session
from models.project import Project
from models.citation import Citation
from models.project_citation import ProjectCitation

class ProjectRepository:
    """
    Repository class for managing Project entities and their operations.
    Handles CRUD operations and relationships with citations through project_citation association.
    """
    
    def __init__(self, db: Session):
        """
        Initialize the repository with a database session.
        
        Args:
            db (Session): SQLAlchemy database session
        """
        self.db = db

    def create(self, name: str) -> Project:
        """
        Create a new project with the given name.
        
        Args:
            name (str): The name of the project to create
            
        Returns:
            Project: The newly created project instance
        """
        project = Project(name=name)
        self.db.add(project)
        self.db.commit()
        self.db.refresh(project)
        return project
    
    def get_by_id(self, project_id: int) -> Project | None:
        """
        Retrieve a project by its ID.
        
        Args:
            project_id (int): The ID of the project to retrieve
            
        Returns:
            Project | None: The project if found, None otherwise
        """
        return self.db.query(Project).filter(Project.id == project_id).first()
    
    def get_all(self) -> list[Project]:
        """
        Retrieve all projects from the database.
        
        Returns:
            list[Project]: List of all projects
        """
        return self.db.query(Project).all()
    
    def update(self, project_id: int, **kwargs) -> Project | None:
        """
        Update a project with the provided key-value pairs.
        
        Args:
            project_id (int): The ID of the project to update
            **kwargs: Key-value pairs of attributes to update
            
        Returns:
            Project | None: The updated project if found, None otherwise
        """
        project = self.get_by_id(project_id)

        if not project:
            return None
        
        # Update only non-None values and existing attributes
        for key, value in kwargs.items():
            if value is None:
                continue

            if hasattr(project, key):
                setattr(project, key, value)

                
        self.db.commit()
        self.db.refresh(project)
        return project   

    def get_all_by_project(self, project_id: int) -> list[Citation]:
        """
        Retrieve all citations associated with a specific project.
        Citations are ordered by year in descending order.
        
        Args:
            project_id (int): The ID of the project
            
        Returns:
            list[Citation]: List of citations associated with the project
        """
        return (
            self.db.query(Citation)
            .join(ProjectCitation, Citation.id == ProjectCitation.citation_id)
            .filter(ProjectCitation.project_id == project_id)
            .order_by(Citation.year.desc())
            .all()
        )      

    def delete(self, project_id: int) -> bool:
        """
        Delete a project and handle associated citations.
        If a citation is only associated with this project, it will also be deleted.
        
        Args:
            project_id (int): The ID of the project to delete
            
        Returns:
            bool: True if deletion was successful, False if project not found
        """
        project = self.get_by_id(project_id)

        if not project:
            return False

        # Get all project-citation associations for this project
        project_associations = (
            self.db.query(ProjectCitation)
            .filter(ProjectCitation.project_id == project_id)
            .all()
        )
        
        # Process each association
        for assoc in project_associations:
            citation_id = assoc.citation_id
            
            # Remove the association
            self.db.delete(assoc)
            
            # Check if this citation is associated with other projects
            remaining_assocs = (
                self.db.query(ProjectCitation)
                .filter(
                    ProjectCitation.citation_id == citation_id,
                    ProjectCitation.project_id != project_id 
                )
                .count()
            )
            
            # If no other projects use this citation, delete it
            if remaining_assocs == 0:
                citation = (
                    self.db.query(Citation)
                    .filter(Citation.id == citation_id)
                    .first()
                )
                if citation:
                    self.db.delete(citation)
        
        # Delete the project itself
        self.db.delete(project)
        self.db.commit()
        return True

    def get_by_name(self, name: str):
        """
        Retrieve a project by its name.
        
        Args:
            name (str): The name of the project to retrieve
            
        Returns:
            Project | None: The project if found, None otherwise
        """
        return self.db.query(Project).filter(Project.name == name).first()