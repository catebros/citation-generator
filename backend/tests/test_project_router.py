# tests/test_project_router_fixed.py
import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock
from datetime import datetime
from main import app
from dependencies import get_project_service
from fastapi import HTTPException

client = TestClient(app)

def test_create_project_success():
    """Test POST /projects creates a project correctly."""
    # Configure mock
    mock_service = MagicMock()
    
    # Simulate created project
    mock_project = MagicMock()
    mock_project.id = 1
    mock_project.name = "Unique Test Project 123"
    mock_project.created_at = datetime.now()
    mock_service.create_project.return_value = mock_project
    
    # Override dependency
    app.dependency_overrides[get_project_service] = lambda: mock_service
    
    try:
        # Hacer request
        response = client.post("/projects", json={"name": "Unique Test Project 123"})
        
        assert response.status_code == 201
        data = response.json()
        assert "id" in data
        assert "name" in data
        assert "created_at" in data
    finally:
        # Cleanup
        app.dependency_overrides.clear()

def test_get_all_projects_success():
    """Test GET /projects returns list of projects."""
    mock_service = MagicMock()
    
    # Simulate project list
    mock_projects = [
        MagicMock(id=1, name="Project 1", created_at=datetime.now()),
        MagicMock(id=2, name="Project 2", created_at=datetime.now())
    ]
    mock_service.get_all_projects.return_value = mock_projects
    
    # Override dependency
    app.dependency_overrides[get_project_service] = lambda: mock_service
    
    try:
        response = client.get("/projects")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 2
    finally:
        # Cleanup
        app.dependency_overrides.clear()

def test_get_project_by_id_success():
    """Test GET /projects/{id} returns existing project."""
    mock_service = MagicMock()
    
    mock_project = MagicMock()
    mock_project.id = 1
    mock_project.name = "Test Project"
    mock_project.created_at = datetime.now()
    mock_service.get_project.return_value = mock_project
    
    # Override dependency
    app.dependency_overrides[get_project_service] = lambda: mock_service
    
    try:
        response = client.get("/projects/1")
        
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert data["name"] == "Test Project"
        assert "created_at" in data
    finally:
        # Cleanup
        app.dependency_overrides.clear()

def test_update_project_success():
    """Test PUT /projects/{id} updates name correctly."""
    mock_service = MagicMock()
    
    mock_project = MagicMock()
    mock_project.id = 1
    mock_project.name = "Updated Project"
    mock_project.created_at = datetime.now()
    mock_service.update_project.return_value = mock_project
    
    # Override dependency
    app.dependency_overrides[get_project_service] = lambda: mock_service
    
    try:
        response = client.put("/projects/1", json={"name": "Updated Project"})
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Project"
    finally:
        # Cleanup
        app.dependency_overrides.clear()

def test_delete_project_success():
    """Test DELETE /projects/{id} deletes correctly."""
    mock_service = MagicMock()
    
    mock_service.delete_project.return_value = {"message": "Project deleted"}
    
    # Override dependency
    app.dependency_overrides[get_project_service] = lambda: mock_service
    
    try:
        response = client.delete("/projects/1")
        
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Project deleted"
    finally:
        # Cleanup
        app.dependency_overrides.clear()

def test_generate_bibliography_success():
    """Test GET /projects/{id}/bibliography returns bibliography."""
    mock_service = MagicMock()
    
    bibliography_data = {
        "project_id": 1,
        "format_type": "apa",
        "bibliography": ["Citation 1", "Citation 2"],
        "citation_count": 2
    }
    mock_service.generate_bibliography_by_project.return_value = bibliography_data
    
    # Override dependency
    app.dependency_overrides[get_project_service] = lambda: mock_service
    
    try:
        response = client.get("/projects/1/bibliography?format_type=apa")
        
        assert response.status_code == 200
        data = response.json()
        assert data["project_id"] == 1
        assert data["format_type"] == "apa"
        assert data["citation_count"] == 2
    finally:
        # Cleanup
        app.dependency_overrides.clear()

def test_get_project_citations_success():
    """Test GET /projects/{id}/citations returns list of citations."""
    mock_service = MagicMock()
    
    # Create citation mock objects with correct structure
    mock_citation1 = MagicMock()
    mock_citation1.id = 1
    mock_citation1.type = "book"
    mock_citation1.title = "Book 1"
    mock_citation1.authors = '["Author Smith"]'  # JSON string
    mock_citation1.year = 2023
    mock_citation1.journal = None
    
    mock_citation2 = MagicMock()
    mock_citation2.id = 2
    mock_citation2.type = "article"
    mock_citation2.title = "Article 1"
    mock_citation2.authors = '["Author Jones"]'  # JSON string
    mock_citation2.year = 2024
    mock_citation2.journal = "Test Journal"
    
    citations = [mock_citation1, mock_citation2]
    mock_service.get_all_citations_by_project.return_value = citations
    
    # Override dependency
    app.dependency_overrides[get_project_service] = lambda: mock_service
    
    try:
        response = client.get("/projects/1/citations")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["title"] == "Book 1"
    finally:
        # Cleanup
        app.dependency_overrides.clear()

# Error cases

def test_create_project_without_name():
    """Test POST without name returns 400."""
    mock_service = MagicMock()
    
    mock_service.create_project.side_effect = HTTPException(
        status_code=400, detail="Missing required project fields: name"
    )
    
    # Override dependency
    app.dependency_overrides[get_project_service] = lambda: mock_service
    
    try:
        response = client.post("/projects", json={})
        
        assert response.status_code == 400
        assert "Missing required project fields" in response.json()["detail"]
    finally:
        # Cleanup
        app.dependency_overrides.clear()

def test_create_project_duplicate_name():
    """Test POST with duplicate name returns 409."""
    mock_service = MagicMock()
    
    mock_service.create_project.side_effect = HTTPException(
        status_code=409, detail="A project with the name 'Existing Project' already exists"
    )
    
    # Override dependency
    app.dependency_overrides[get_project_service] = lambda: mock_service
    
    try:
        response = client.post("/projects", json={"name": "Existing Project"})
        
        assert response.status_code == 409
        assert "already exists" in response.json()["detail"]
    finally:
        # Cleanup
        app.dependency_overrides.clear()

def test_get_project_not_found():
    """Test GET /projects/{id} with nonexistent ID returns 404."""
    mock_service = MagicMock()
    
    mock_service.get_project.side_effect = HTTPException(
        status_code=404, detail="Project not found"
    )
    
    # Override dependency
    app.dependency_overrides[get_project_service] = lambda: mock_service
    
    try:
        response = client.get("/projects/999")
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]
    finally:
        # Cleanup
        app.dependency_overrides.clear()

def test_update_project_not_found():
    """Test PUT /projects/{id} with nonexistent ID returns 404."""
    mock_service = MagicMock()
    
    mock_service.update_project.side_effect = HTTPException(
        status_code=404, detail="Project not found"
    )
    
    # Override dependency
    app.dependency_overrides[get_project_service] = lambda: mock_service
    
    try:
        response = client.put("/projects/999", json={"name": "New Name"})
        
        assert response.status_code == 404
    finally:
        # Cleanup
        app.dependency_overrides.clear()

def test_delete_project_not_found():
    """Test DELETE /projects/{id} nonexistent returns 404."""
    mock_service = MagicMock()
    
    mock_service.delete_project.side_effect = HTTPException(
        status_code=404, detail="Project not found"
    )
    
    # Override dependency
    app.dependency_overrides[get_project_service] = lambda: mock_service
    
    try:
        response = client.delete("/projects/999")
        
        assert response.status_code == 404
    finally:
        # Cleanup
        app.dependency_overrides.clear()

def test_bibliography_project_not_found():
    """Test bibliography with nonexistent project returns 404."""
    mock_service = MagicMock()
    
    mock_service.generate_bibliography_by_project.side_effect = HTTPException(
        status_code=404, detail="Project not found"
    )
    
    # Override dependency
    app.dependency_overrides[get_project_service] = lambda: mock_service
    
    try:
        response = client.get("/projects/999/bibliography")
        
        assert response.status_code == 404
    finally:
        # Cleanup
        app.dependency_overrides.clear()

def test_internal_server_error():
    """Test simulated internal errors return 500."""
    mock_service = MagicMock()
    
    mock_service.get_project.side_effect = Exception("Database error")
    
    # Override dependency
    app.dependency_overrides[get_project_service] = lambda: mock_service
    
    try:
        response = client.get("/projects/1")
        
        assert response.status_code == 500
        assert "Internal server error" in response.json()["detail"]
    finally:
        # Cleanup
        app.dependency_overrides.clear()

def test_get_project_citations_not_found():
    """Test GET /projects/{id}/citations with nonexistent project."""
    mock_service = MagicMock()
    
    mock_service.get_all_citations_by_project.side_effect = HTTPException(
        status_code=404, detail="Project not found"
    )
    
    # Override dependency
    app.dependency_overrides[get_project_service] = lambda: mock_service
    
    try:
        response = client.get("/projects/999/citations")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]
    finally:
        # Cleanup
        app.dependency_overrides.clear()

def test_bibliography_invalid_format():
    """Test GET /projects/{id}/bibliography with invalid format_type."""
    mock_service = MagicMock()
    
    mock_service.generate_bibliography_by_project.side_effect = HTTPException(
        status_code=400, detail="Unsupported format: invalid. Supported formats: 'apa', 'mla'"
    )
    
    # Override dependency
    app.dependency_overrides[get_project_service] = lambda: mock_service
    
    try:
        response = client.get("/projects/1/bibliography?format_type=invalid")
        assert response.status_code == 400
        assert "Unsupported format" in response.json()["detail"]
    finally:
        # Cleanup
        app.dependency_overrides.clear()

def test_get_project_citations_empty_list():
    """Test GET /projects/{id}/citations when there are no citations."""
    mock_service = MagicMock()
    
    # Simular proyecto existente pero sin citas
    mock_service.get_all_citations_by_project.return_value = []
    
    # Override dependency
    app.dependency_overrides[get_project_service] = lambda: mock_service
    
    try:
        response = client.get("/projects/1/citations")
        assert response.status_code == 200
        data = response.json()
        assert data == []
        assert len(data) == 0
    finally:
        # Cleanup
        app.dependency_overrides.clear()