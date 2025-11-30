# backend/tests/test_main.py
"""
Test suite for main FastAPI application endpoints.

This module tests the core application endpoints:
- Root endpoint (/) - API status and basic info
- Health check endpoint (/health) - System health verification
- API documentation endpoints (/docs, /redoc)
- Error handling for invalid routes

These tests verify basic API infrastructure is working.
"""
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_root_endpoint():
    """Test GET / returns 200 and expected message."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "Citation Generator API is running" in data["message"]
    assert data["status"] == "healthy"
    assert data["version"] == "1.0.0"

def test_health_check():
    """Test GET /health returns 200 and JSON includes expected fields."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["database"] == "connected"
    assert data["api_version"] == "1.0.0"
    assert "APA" in data["supported_formats"]
    assert "MLA" in data["supported_formats"]
    assert "article" in data["citation_types"]
    assert "book" in data["citation_types"]
    assert "website" in data["citation_types"]
    assert "report" in data["citation_types"]

def test_openapi_docs():
    """Test OpenAPI docs (/docs) load without error."""
    response = client.get("/docs")
    assert response.status_code == 200


def test_redoc_docs():
    """Test ReDoc (/redoc) loads without error."""
    response = client.get("/redoc")
    assert response.status_code == 200

def test_invalid_endpoint():
    """Test non-existent endpoint returns 404."""
    response = client.get("/invalid-endpoint")
    assert response.status_code == 404


def test_exception_handling():
    """Test basic exception handling."""
    # Verify framework handles exceptions appropriately
    response = client.get("/nonexistent-route")
    assert response.status_code == 404