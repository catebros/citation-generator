# tests/test_citation_router_fixed.py
from datetime import datetime
from unittest.mock import MagicMock

from dependencies import get_citation_service
from fastapi import HTTPException
from fastapi.testclient import TestClient
from main import app
from models.citation import Citation

client = TestClient(app)

# Success cases


def test_create_citation_success():
    """Test POST /projects/{id}/citations creates a valid citation."""
    # Setup mock service
    mock_service = MagicMock()

    # Simulate created citation with all required fields for book
    created_citation = Citation(
        id=1,
        type="book",
        authors='["John Doe"]',  # Authors as JSON string
        title="Test Book",
        year=2023,
        publisher="Test Publisher",
        place="New York",
        edition=1,
        created_at=datetime.now(),
    )
    mock_service.create_citation.return_value = created_citation

    # Override dependency
    app.dependency_overrides[get_citation_service] = lambda: mock_service

    try:
        # Citation data with all required fields for book
        citation_data = {
            "type": "book",
            "authors": ["John Doe"],  # Authors as list
            "title": "Test Book",
            "year": 2023,
            "publisher": "Test Publisher",
            "place": "New York",
            "edition": 1,
        }

        response = client.post("/projects/1/citations", json=citation_data)

        assert response.status_code == 201
        data = response.json()
        assert data["id"] == 1
        assert data["type"] == "book"
        assert data["authors"] == ["John Doe"]  # Should be returned as list
        assert data["title"] == "Test Book"
        assert data["year"] == 2023
        assert data["publisher"] == "Test Publisher"
        assert data["place"] == "New York"
        assert data["edition"] == 1
    finally:
        # Clean up dependency override
        app.dependency_overrides.clear()


def test_get_citation_by_id_success():
    """Test GET /citations/{id} returns existing citation."""
    # Setup mock service
    mock_service = MagicMock()

    # Citation with all required fields for article
    citation = Citation(
        id=1,
        type="article",
        authors='["Jane Smith"]',  # Authors as JSON string
        title="Test Article",
        year=2023,
        journal="Test Journal",
        volume=15,
        issue="2",
        pages="10-20",
        doi="10.1000/test",
        created_at=datetime.now(),
    )
    mock_service.get_citation.return_value = citation

    # Override dependency
    app.dependency_overrides[get_citation_service] = lambda: mock_service

    try:
        response = client.get("/citations/1")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == 1
        assert data["type"] == "article"
        assert data["authors"] == ["Jane Smith"]  # Should be returned as list
        assert data["title"] == "Test Article"
        assert data["year"] == 2023
        assert data["journal"] == "Test Journal"
        assert data["volume"] == 15
        assert data["issue"] == "2"
        assert data["pages"] == "10-20"
        assert data["doi"] == "10.1000/test"
    finally:
        # Clean up dependency override
        app.dependency_overrides.clear()


def test_update_citation_success():
    """Test PUT /projects/{id}/citations/{id} updates correctly."""
    # Setup mock service
    mock_service = MagicMock()

    # Citation actualizada con todos los campos requeridos
    updated_citation = Citation(
        id=1,
        type="book",
        authors='["John Doe"]',  # Authors as JSON string
        title="Updated Book Title",
        year=2024,
        publisher="Test Publisher",
        place="New York",
        edition=1,
        created_at=datetime.now(),
    )
    mock_service.update_citation.return_value = updated_citation

    # Override dependency
    app.dependency_overrides[get_citation_service] = lambda: mock_service

    try:
        update_data = {"title": "Updated Book Title", "year": 2024}

        response = client.put("/projects/1/citations/1", json=update_data)

        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Updated Book Title"
        assert data["year"] == 2024
        assert data["authors"] == ["John Doe"]  # Should be returned as list
    finally:
        # Clean up dependency override
        app.dependency_overrides.clear()


def test_delete_citation_success():
    """Test DELETE /projects/{id}/citations/{id} returns message."""
    # Setup mock service
    mock_service = MagicMock()
    mock_service.delete_citation.return_value = {"message": "Citation deleted"}

    # Override dependency
    app.dependency_overrides[get_citation_service] = lambda: mock_service

    try:
        response = client.delete("/projects/1/citations/1")

        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Citation deleted"
    finally:
        # Clean up dependency override
        app.dependency_overrides.clear()


# Error cases


def test_create_citation_project_not_found():
    """Test POST with nonexistent project returns 404."""
    # Setup mock service
    mock_service = MagicMock()
    mock_service.create_citation.side_effect = HTTPException(
        status_code=404, detail="Project not found"
    )

    # Override dependency
    app.dependency_overrides[get_citation_service] = lambda: mock_service

    try:
        citation_data = {
            "type": "book",
            "authors": ["John Doe"],
            "title": "Test Book",
            "year": 2023,
            "publisher": "Test Publisher",
            "place": "New York",
            "edition": 1,
        }

        response = client.post("/projects/999/citations", json=citation_data)

        assert response.status_code == 404
        assert "not found" in response.json()["detail"]
    finally:
        # Clean up dependency override
        app.dependency_overrides.clear()


def test_create_citation_missing_required_fields():
    """Test POST without required fields returns 400."""
    # Setup mock service
    mock_service = MagicMock()
    error_detail = "Missing required book fields: place, edition"
    mock_service.create_citation.side_effect = HTTPException(
        status_code=400, detail=error_detail
    )

    # Override dependency
    app.dependency_overrides[get_citation_service] = lambda: mock_service

    try:
        citation_data = {
            "type": "book",
            "authors": ["John Doe"],
            "title": "Test Book",
            "year": 2023,
            "publisher": "Test Publisher",
            # Missing: place, edition
        }

        response = client.post("/projects/1/citations", json=citation_data)

        assert response.status_code == 400
        assert "Missing required" in response.json()["detail"]
    finally:
        # Clean up dependency override
        app.dependency_overrides.clear()


def test_create_citation_unsupported_type():
    """Test POST with unsupported type returns 400."""
    # Setup mock service
    mock_service = MagicMock()
    mock_service.create_citation.side_effect = HTTPException(
        status_code=400, detail="Unsupported citation type: unsupported"
    )

    # Override dependency
    app.dependency_overrides[get_citation_service] = lambda: mock_service

    try:
        citation_data = {
            "type": "unsupported",
            "authors": ["John Doe"],
            "title": "Test Document",
        }

        response = client.post("/projects/1/citations", json=citation_data)

        assert response.status_code == 400
        assert "Unsupported citation type" in response.json()["detail"]
    finally:
        # Clean up dependency override
        app.dependency_overrides.clear()


def test_get_citation_not_found():
    """Test GET with nonexistent citation returns 404."""
    # Setup mock service
    mock_service = MagicMock()
    mock_service.get_citation.side_effect = HTTPException(
        status_code=404, detail="Citation not found"
    )

    # Override dependency
    app.dependency_overrides[get_citation_service] = lambda: mock_service

    try:
        response = client.get("/citations/999")

        assert response.status_code == 404
        assert "not found" in response.json()["detail"]
    finally:
        # Clean up dependency override
        app.dependency_overrides.clear()


def test_update_citation_project_not_found():
    """Test PUT with nonexistent project."""
    mock_service = MagicMock()
    mock_service.update_citation.side_effect = HTTPException(
        status_code=404, detail="Project not found"
    )

    # Override dependency
    app.dependency_overrides[get_citation_service] = lambda: mock_service

    try:
        update_url = "/projects/999/citations/1"
        response = client.put(update_url, json={"title": "Updated Title"})
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]
    finally:
        # Clean up dependency override
        app.dependency_overrides.clear()


def test_delete_citation_not_found():
    """Test DELETE with nonexistent citation."""
    mock_service = MagicMock()
    mock_service.delete_citation.side_effect = HTTPException(
        status_code=404, detail="Citation not found"
    )

    # Override dependency
    app.dependency_overrides[get_citation_service] = lambda: mock_service

    try:
        delete_url = "/projects/1/citations/999"
        response = client.delete(delete_url)
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]
    finally:
        # Clean up dependency override
        app.dependency_overrides.clear()


def test_update_citation_invalid_data():
    """Test PUT with invalid field."""
    mock_service = MagicMock()
    mock_service.update_citation.side_effect = HTTPException(
        status_code=400, detail="Invalid DOI format"
    )

    # Override dependency
    app.dependency_overrides[get_citation_service] = lambda: mock_service

    try:
        response = client.put("/projects/1/citations/1", json={"doi": "invalid-doi"})
        assert response.status_code == 400
        assert "Invalid DOI" in response.json()["detail"]
    finally:
        # Clean up dependency override
        app.dependency_overrides.clear()


def test_get_citation_internal_error():
    """Test GET /citations/{id} when there is internal error."""
    mock_service = MagicMock()
    mock_service.get_citation.side_effect = Exception("Database connection lost")

    # Override dependency
    app.dependency_overrides[get_citation_service] = lambda: mock_service

    try:
        response = client.get("/citations/1")
        assert response.status_code == 500
        assert "Internal server error" in response.json()["detail"]
    finally:
        # Clean up dependency override
        app.dependency_overrides.clear()
