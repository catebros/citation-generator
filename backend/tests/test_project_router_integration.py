# tests/test_project_router_integration.py
import uuid

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

# Real integration tests (no mocks)


def test_create_project_integration():
    """Real integration test: create project with unique name."""
    unique_name = f"Test Project {uuid.uuid4().hex[:8]}"

    response = client.post("/projects", json={"name": unique_name})

    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert data["name"] == unique_name
    assert "created_at" in data


def test_get_all_projects_integration():
    """Real integration test: get all projects."""
    response = client.get("/projects")

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_project_lifecycle_integration():
    """Test complete cycle: create, read, update, delete project."""
    unique_name = f"Lifecycle Project {uuid.uuid4().hex[:8]}"

    # 1. Create project
    create_response = client.post("/projects", json={"name": unique_name})
    assert create_response.status_code == 201
    project_id = create_response.json()["id"]

    # 2. Read project
    get_response = client.get(f"/projects/{project_id}")
    assert get_response.status_code == 200
    assert get_response.json()["name"] == unique_name

    # 3. Update project
    new_name = f"Updated {unique_name}"
    update_response = client.put(f"/projects/{project_id}", json={"name": new_name})
    assert update_response.status_code == 200
    assert update_response.json()["name"] == new_name

    # 4. Delete project
    delete_response = client.delete(f"/projects/{project_id}")
    assert delete_response.status_code == 200
    assert "deleted" in delete_response.json()["message"]

    # 5. Verify it was deleted
    get_deleted_response = client.get(f"/projects/{project_id}")
    assert get_deleted_response.status_code == 404


# Error case tests


def test_create_project_without_name():
    """Test create project without name."""
    response = client.post("/projects", json={})

    assert response.status_code == 400
    assert (
        "name" in response.json()["detail"]
        or "Missing required" in response.json()["detail"]
    )


def test_create_project_duplicate_name():
    """Test create project with duplicate name."""
    unique_name = f"Duplicate Test {uuid.uuid4().hex[:8]}"

    # Create the first project
    response1 = client.post("/projects", json={"name": unique_name})
    assert response1.status_code == 201

    # Attempt to create the second with the same name
    response2 = client.post("/projects", json={"name": unique_name})
    assert response2.status_code == 409
    assert "already exists" in response2.json()["detail"]


def test_get_nonexistent_project():
    """Test get project that doesn't exist."""
    response = client.get("/projects/99999")

    assert response.status_code == 404
    assert "not found" in response.json()["detail"]


def test_update_nonexistent_project():
    """Test update project that doesn't exist."""
    response = client.put("/projects/99999", json={"name": "New Name"})

    assert response.status_code == 404


def test_delete_nonexistent_project():
    """Test delete project that doesn't exist."""
    response = client.delete("/projects/99999")

    assert response.status_code == 404
