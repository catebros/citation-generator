"""
Database Population Script
This script populates the database with sample data for testing and demonstration purposes.
Run this script after setting up the database to have sample projects and citations.
"""

from db.database import get_session_factory, engine
from models.base import Base
from services.project_service import ProjectService
from services.citation_service import CitationService
import sys
import traceback


def populate_database():
    """Populate the database with sample data using API services."""

    # Create database tables if they don't exist
    Base.metadata.create_all(bind=engine)

    # Create database session
    session_factory = get_session_factory()
    session = session_factory()
    
    try:
        # Initialize services
        project_service = ProjectService(session)
        citation_service = CitationService(session)
        
        print("Starting database population...")
        
        # Sample projects data
        projects_data = [
            {"name": "Academic Research Project"},
            {"name": "Literature Review Study"},
            {"name": "Thesis Bibliography"},
            {"name": "Technical Documentation"}
        ]
        
        # Create projects
        projects = []
        for project_data in projects_data:
            try:
                project = project_service.create_project(project_data)
                projects.append(project)
                print(f"Created project: {project.name}")
            except Exception as e:
                print(f"Error creating project {project_data['name']}: {e}")
                if hasattr(e, 'detail'):
                    print(f"  Detail: {e.detail}")
                traceback.print_exc()
        
        # Sample citations data for different types
        citations_data = [
            # Book citations
            {
                "type": "book",
                "title": "Introduction to Machine Learning",
                "authors": ["John Smith", "Mary Johnson"],
                "year": 2023,
                "publisher": "Academic Press",
                "place": "New York",
                "edition": 3
            },
            {
                "type": "book",
                "title": "Data Science Fundamentals",
                "authors": ["Alice Brown", "Robert Davis"],
                "year": 2022,
                "publisher": "Tech Publications",
                "place": "Boston",
                "edition": 1
            },
            {
                "type": "book",
                "title": "Artificial Intelligence: A Modern Approach",
                "authors": ["Stuart Russell", "Peter Norvig"],
                "year": 2021,
                "publisher": "Pearson Education",
                "place": "London",
                "edition": 4
            },
            
            # Article citations
            {
                "type": "article",
                "title": "Deep Learning in Natural Language Processing",
                "authors": ["James Wilson", "Sarah Taylor"],
                "year": 2023,
                "journal": "Journal of AI Research",
                "volume": 45,
                "issue": "3",
                "pages": "123-145",
                "doi": "10.1234/jair.2023.123"
            },
            {
                "type": "article",
                "title": "Neural Networks and Computer Vision",
                "authors": ["Michael Anderson", "Lisa Thompson"],
                "year": 2022,
                "journal": "Computer Vision Quarterly",
                "volume": 28,
                "issue": "2",
                "pages": "67-89",
                "doi": "10.5678/cvq.2022.067"
            },
            {
                "type": "article",
                "title": "Machine Learning Applications in Healthcare",
                "authors": ["Elena Garcia", "Carlos Martinez"],
                "year": 2023,
                "journal": "Medical Informatics Review",
                "volume": 12,
                "issue": "4",
                "pages": "201-225",
                "doi": "10.9012/mir.2023.201"
            },
            
            # Website citations
            {
                "type": "website",
                "title": "Python Programming Tutorial",
                "authors": ["Guido van Rossum"],
                "year": 2023,
                "publisher": "Python.org",
                "url": "https://docs.python.org/3/tutorial/",
                "access_date": "2023-12-01"
            },
            {
                "type": "website",
                "title": "FastAPI Documentation",
                "authors": ["Sebastian Ramirez"],
                "year": 2023,
                "publisher": "FastAPI",
                "url": "https://fastapi.tiangolo.com/",
                "access_date": "2023-11-15"
            },
            {
                "type": "website",
                "title": "Machine Learning Best Practices",
                "authors": ["Jeff Dean", "Andrew Ng"],
                "year": 2023,
                "publisher": "Google Developers",
                "url": "https://developers.google.com/machine-learning/guides",
                "access_date": "2023-10-20"
            },
            
            # Report citations
            {
                "type": "report",
                "title": "State of AI Technology Report 2023",
                "authors": ["Daniel Chen", "Rachel Kim"],
                "year": 2023,
                "publisher": "Global Tech Foundation",
                "url": "https://techreport.org/ai-2023",
                "place": "San Francisco"
            },
            {
                "type": "report",
                "title": "Cybersecurity Trends Analysis",
                "authors": ["Marcus Johnson", "Priya Patel"],
                "year": 2022,
                "publisher": "InfoSec Publications",
                "url": "https://infosec.com/trends-2022",
                "place": "Washington DC"
            },
            {
                "type": "report",
                "title": "Digital Transformation in Education",
                "authors": ["Emma Rodriguez", "David Lee"],
                "year": 2023,
                "publisher": "Education Research Foundation",
                "url": "https://erf.org/digital-transformation-2023",
                "place": "Chicago"
            }
        ]
        
        # Create citations and associate with projects
        created_citations = []
        
        # Project-Citation assignments (project index: [citation indices])
        project_assignments = {
            0: [0, 3, 6, 9],    # Academic Research Project: ML book, DL article, Python docs, AI report
            1: [1, 4, 7, 10],   # Literature Review Study: DS book, CV article, FastAPI docs, Security report
            2: [2, 5, 8, 11],   # Thesis Bibliography: AI book, Healthcare article, ML guide, Education report
            3: [0, 1, 3, 4]     # Technical Documentation: mix of books and articles
        }
        
        for i, citation_data in enumerate(citations_data):
            try:
                # Find which projects should have this citation
                target_projects = []
                for project_idx, citation_indices in project_assignments.items():
                    if i in citation_indices and project_idx < len(projects):
                        target_projects.append(projects[project_idx])
                
                # Create citation in the first target project
                if target_projects:
                    citation = citation_service.create_citation(target_projects[0].id, citation_data)
                    created_citations.append(citation)
                    print(f"Created citation: {citation.title}")
                    
                    # Associate with additional projects if needed
                    for additional_project in target_projects[1:]:
                        try:
                            citation_service.create_citation(additional_project.id, citation_data)
                            print(f"Associated citation '{citation.title}' with project '{additional_project.name}'")
                        except Exception as e:
                            # If citation already exists, it will be reused automatically
                            print(f"Citation '{citation.title}' already exists in project '{additional_project.name}'")
                
            except Exception as e:
                print(f"Error creating citation '{citation_data['title']}': {e}")
        
        # Print summary
        print("\nDatabase Population Summary:")
        print(f"Projects created: {len(projects)}")
        print(f"Citations created: {len(created_citations)}")
        
        citation_types = {}
        for citation_data in citations_data:
            citation_type = citation_data["type"]
            citation_types[citation_type] = citation_types.get(citation_type, 0) + 1
        
        for citation_type, count in citation_types.items():
            print(f"  - {citation_type.capitalize()}s: {count}")
        
        print("\nSample Projects:")
        for i, project in enumerate(projects):
            assignment_count = len([idx for idx, citations in project_assignments.items() if idx == i])
            if assignment_count > 0:
                citation_count = len(project_assignments.get(i, []))
                print(f"  {i+1}. {project.name} ({citation_count} citations)")
        
        print("\nDatabase populated successfully!")
        
    except Exception as e:
        session.rollback()
        print(f"Error populating database: {str(e)}")
        raise
    finally:
        session.close()


def clear_database():
    """Clear all data from the database using API services."""
    
    # Create database session
    session_factory = get_session_factory()
    session = session_factory()
    
    try:
        # Initialize services
        project_service = ProjectService(session)
        
        print("Clearing database...")
        
        # Get all projects and delete them (this should cascade to citations)
        projects = project_service.get_all_projects()
        for project in projects:
            try:
                project_service.delete_project(project.id)
                print(f"Deleted project: {project.name}")
            except Exception as e:
                print(f"Error deleting project {project.name}: {e}")
        
        print("Database cleared successfully!")
        
    except Exception as e:
        session.rollback()
        print(f"Error clearing database: {str(e)}")
        raise
    finally:
        session.close()


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--clear":
        print("Clearing database...")
        clear_database()
    else:
        print("Populating database with sample data...")
        populate_database()
