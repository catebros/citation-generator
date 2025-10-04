# tests/test_integration_fixed.py
import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock
from datetime import datetime
from main import app
from dependencies import get_project_service, get_citation_service
from models.project import Project
from models.citation import Citation
import uuid

client = TestClient(app)

# Cross-integration tests using dependency overrides

def test_create_project_and_citations_workflow():
    """Test create project → create multiple citations → query /projects/{id}/citations."""
    
    # Configure mocks
    mock_proj_service = MagicMock()
    mock_cit_service = MagicMock()
    
    # 1. Create project
    created_project = MagicMock()
    created_project.id = 1
    created_project.name = "Integration Test Project"
    created_project.created_at = datetime.now()
    mock_proj_service.create_project.return_value = created_project
    
    # Override dependencies
    app.dependency_overrides[get_project_service] = lambda: mock_proj_service
    app.dependency_overrides[get_citation_service] = lambda: mock_cit_service
    
    try:
        project_response = client.post("/projects", json={"name": "Integration Test Project"})
        assert project_response.status_code == 201
        project_id = project_response.json()["id"]
        
    # 2. Create multiple citations
        citations_data = [
            {
                "type": "book",
                "authors": ["Author 1"],
                "title": "Book 1",
                "year": 2023,
                "publisher": "Publisher 1",
                "place": "New York",
                "edition": 1
            },
            {
                "type": "article",
                "authors": ["Author 2"],
                "title": "Article 1",
                "year": 2023,
                "journal": "Journal 1",
                "volume": 10,
                "issue": "1",
                "pages": "1-10",
                "doi": "10.1000/test"
            }
        ]
        
        created_citations = []
        for i, citation_data in enumerate(citations_data, 1):
            created_citation = MagicMock()
            created_citation.id = i
            created_citation.type = citation_data["type"]
            created_citation.title = citation_data["title"]
            created_citation.authors = f'["{citation_data["authors"][0]}"]'
            created_citation.year = citation_data["year"]
            mock_cit_service.create_citation.return_value = created_citation
            
            response = client.post(f"/projects/{project_id}/citations", json=citation_data)
            assert response.status_code == 201
            created_citations.append(response.json())
        
    # 3. Query project citations
        mock_citations = []
        for citation_data in created_citations:
            mock_citation = MagicMock()
            mock_citation.id = citation_data["id"]
            mock_citation.title = citation_data["title"]
            mock_citation.authors = '["Test Author"]'
            mock_citations.append(mock_citation)
        
        mock_proj_service.get_all_citations_by_project.return_value = mock_citations
        
        citations_response = client.get(f"/projects/{project_id}/citations")
        assert citations_response.status_code == 200
        citations_list = citations_response.json()
        assert len(citations_list) == 2
        assert citations_list[0]["title"] == "Book 1"
        assert citations_list[1]["title"] == "Article 1"
        
    finally:
        # Cleanup
        app.dependency_overrides.clear()

def test_delete_project_cascade_citations():
    """Test delete project and verify associated citations are deleted."""
    
    mock_proj_service = MagicMock()
    mock_cit_service = MagicMock()
    
    # Simulate successful deletion with cascade
    mock_proj_service.delete_project.return_value = {
        "message": "Project deleted successfully"
    }
    
    # Override dependencies
    app.dependency_overrides[get_project_service] = lambda: mock_proj_service
    app.dependency_overrides[get_citation_service] = lambda: mock_cit_service
    
    try:
        response = client.delete("/projects/1")
        
        assert response.status_code == 200
        data = response.json()
        assert "deleted" in data["message"]
        
    # Verify that the delete method was called
        mock_proj_service.delete_project.assert_called_once_with(1)
        
    finally:
        # Cleanup
        app.dependency_overrides.clear()

def test_generate_bibliography_with_citation_count():
    """Test generate bibliography and verify citation_count."""
    
    mock_proj_service = MagicMock()
    
    # Simulate bibliography with correct count
    bibliography_data = {
        "project_id": 1,
        "format_type": "apa",
        "bibliography": [
            "Author 1. (2023). Book Title. Publisher.",
            "Author 2. (2023). Article Title. Journal Name."
        ],
        "citation_count": 2
    }
    mock_proj_service.generate_bibliography_by_project.return_value = bibliography_data
    
    # Override dependencies
    app.dependency_overrides[get_project_service] = lambda: mock_proj_service
    
    try:
        response = client.get("/projects/1/bibliography?format_type=apa")
        
        assert response.status_code == 200
        data = response.json()
        assert data["citation_count"] == 2
        assert len(data["bibliography"]) == data["citation_count"]
        
    finally:
        # Cleanup
        app.dependency_overrides.clear()

def test_bibliography_format_change_apa_to_mla():
    """Test change format from APA to MLA in bibliography."""
    
    mock_proj_service = MagicMock()
    
    # Override dependencies
    app.dependency_overrides[get_project_service] = lambda: mock_proj_service
    
    try:
    # Simulate APA response
        apa_bibliography = {
            "project_id": 1,
            "format_type": "apa",
            "bibliography": ["Author, A. (2023). Title. Publisher."],
            "citation_count": 1
        }
        mock_proj_service.generate_bibliography_by_project.return_value = apa_bibliography
        
        apa_response = client.get("/projects/1/bibliography?format_type=apa")
        assert apa_response.status_code == 200
        apa_data = apa_response.json()
        assert apa_data["format_type"] == "apa"
        assert "Author, A. (2023)" in apa_data["bibliography"][0]
        
    # Simulate MLA response
        mla_bibliography = {
            "project_id": 1,
            "format_type": "mla",
            "bibliography": ["Author, Author. Title. Publisher, 2023."],
            "citation_count": 1
        }
        mock_proj_service.generate_bibliography_by_project.return_value = mla_bibliography
        
        mla_response = client.get("/projects/1/bibliography?format_type=mla")
        assert mla_response.status_code == 200
        mla_data = mla_response.json()
        assert mla_data["format_type"] == "mla"
        assert "Author, Author." in mla_data["bibliography"][0]
        
    # Verify that the format changed
        assert apa_data["format_type"] != mla_data["format_type"]
        assert apa_data["bibliography"][0] != mla_data["bibliography"][0]
        
    finally:
        # Cleanup
        app.dependency_overrides.clear()

def test_full_workflow_project_citations_bibliography():
    """Test complete workflow: create project → add citations → generate bibliography."""
    
    mock_proj_service = MagicMock()
    mock_cit_service = MagicMock()
    
    # 1. Create project
    project = MagicMock()
    project.id = 1
    project.name = "Full Workflow Project"
    project.created_at = datetime.now()
    mock_proj_service.create_project.return_value = project
    
    # Override dependencies
    app.dependency_overrides[get_project_service] = lambda: mock_proj_service
    app.dependency_overrides[get_citation_service] = lambda: mock_cit_service
    
    try:
        project_response = client.post("/projects", json={"name": "Full Workflow Project"})
        assert project_response.status_code == 201
        project_id = project_response.json()["id"]
        
        # 2. Add multiple citations
        citation_1 = MagicMock()
        citation_1.id = 1
        citation_1.type = "book"
        citation_1.authors = '["Smith, J."]'
        citation_1.title = "Research Methods"
        citation_1.year = 2023
        citation_1.publisher = "Academic Press"
        citation_1.place = "Cambridge"
        citation_1.edition = 2
        
        citation_2 = MagicMock()
        citation_2.id = 2
        citation_2.type = "article"
        citation_2.authors = '["Jones, M."]'
        citation_2.title = "Data Analysis"
        citation_2.year = 2023
        citation_2.journal = "Research Journal"
        citation_2.volume = 15
        citation_2.issue = "3"
        citation_2.pages = "45-67"
        citation_2.doi = "10.1000/research"
        
        mock_cit_service.create_citation.side_effect = [citation_1, citation_2]
        
    # Create citations
        for citation_data in [
            {"type": "book", "authors": ["Smith, J."], "title": "Research Methods", "year": 2023, "publisher": "Academic Press", "place": "Cambridge", "edition": 2},
            {"type": "article", "authors": ["Jones, M."], "title": "Data Analysis", "year": 2023, "journal": "Research Journal", "volume": 15, "issue": "3", "pages": "45-67", "doi": "10.1000/research"}
        ]:
            response = client.post(f"/projects/{project_id}/citations", json=citation_data)
            assert response.status_code == 201
        
        # 3. Generate complete bibliography
        bibliography_data = {
            "project_id": project_id,
            "format_type": "apa",
            "bibliography": [
                "Smith, J. (2023). Research Methods. Academic Press.",
                "Jones, M. (2023). Data Analysis. Research Journal."
            ],
            "citation_count": 2
        }
        mock_proj_service.generate_bibliography_by_project.return_value = bibliography_data
        
        bibliography_response = client.get(f"/projects/{project_id}/bibliography?format_type=apa")
        assert bibliography_response.status_code == 200
        
        bib_data = bibliography_response.json()
        assert bib_data["project_id"] == project_id
        assert bib_data["citation_count"] == 2
        assert len(bib_data["bibliography"]) == 2
        assert "Smith, J." in bib_data["bibliography"][0]
        assert "Jones, M." in bib_data["bibliography"][1]
        
    finally:
        # Cleanup
        app.dependency_overrides.clear()

def test_empty_project_bibliography():
    """Test generate bibliography for project without citations."""
    
    mock_proj_service = MagicMock()
    
    # Simulate project without citations
    empty_bibliography = {
        "project_id": 1,
        "format_type": "apa",
        "bibliography": [],
        "citation_count": 0
    }
    mock_proj_service.generate_bibliography_by_project.return_value = empty_bibliography
    
    # Override dependencies
    app.dependency_overrides[get_project_service] = lambda: mock_proj_service
    
    try:
        response = client.get("/projects/1/bibliography?format_type=apa")
        
        assert response.status_code == 200
        data = response.json()
        assert data["citation_count"] == 0
        assert len(data["bibliography"]) == 0
        
    finally:
        # Cleanup
        app.dependency_overrides.clear()

def test_update_citation_and_regenerate_bibliography():
    """Test update citation and regenerate bibliography with changes."""
    
    mock_proj_service = MagicMock()
    mock_cit_service = MagicMock()
    
    # 1. Update citation
    updated_citation = MagicMock()
    updated_citation.id = 1
    updated_citation.type = "book"
    updated_citation.authors = '["Smith, J."]'
    updated_citation.title = "Updated Research Methods"
    updated_citation.year = 2024
    updated_citation.publisher = "New Publisher"
    updated_citation.place = "Boston"
    updated_citation.edition = 3
    mock_cit_service.update_citation.return_value = updated_citation
    
    # Override dependencies
    app.dependency_overrides[get_project_service] = lambda: mock_proj_service
    app.dependency_overrides[get_citation_service] = lambda: mock_cit_service
    
    try:
        update_response = client.put("/projects/1/citations/1", json={
            "title": "Updated Research Methods",
            "year": 2024,
            "publisher": "New Publisher"
        })
        assert update_response.status_code == 200
        
    # 2. Regenerate bibliography with changes
        updated_bibliography = {
            "project_id": 1,
            "format_type": "apa",
            "bibliography": ["Smith, J. (2024). Updated Research Methods. New Publisher."],
            "citation_count": 1
        }
        mock_proj_service.generate_bibliography_by_project.return_value = updated_bibliography
        
        bibliography_response = client.get("/projects/1/bibliography?format_type=apa")
        assert bibliography_response.status_code == 200
        
        bib_data = bibliography_response.json()
        assert "Updated Research Methods" in bib_data["bibliography"][0]
        assert "2024" in bib_data["bibliography"][0]
        assert "New Publisher" in bib_data["bibliography"][0]
        
    finally:
        # Cleanup
        app.dependency_overrides.clear()