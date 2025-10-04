# backend/routers/projects.py
"""
Project-related API endpoints.
Handles CRUD operations for projects.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Dict, Any
from dependencies import get_project_service
from services.project_service import ProjectService

router = APIRouter(prefix="/projects", tags=["Projects"])

@router.post("", status_code=status.HTTP_201_CREATED)
def create_project(
    project_data: Dict[str, Any],
    project_service: ProjectService = Depends(get_project_service)
) -> Dict[str, Any]:
    """
    Create a new project.
    
    Args:
        project_data: Project creation data (must include 'name')
        
    Returns:
        Created project with assigned ID
    """
    try:
        project = project_service.create_project(project_data)
        return {
            "id": project.id,
            "name": project.name,
            "created_at": project.created_at.isoformat(),
            "updated_at": project.updated_at.isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("")
def get_all_projects(
    project_service: ProjectService = Depends(get_project_service)
) -> List[Dict[str, Any]]:
    """
    Get all projects.
    
    Returns:
        List of all projects in the system
    """
    try:
        projects = project_service.get_all_projects()
        return [
            {
                "id": project.id,
                "name": project.name,
                "created_at": project.created_at.isoformat(),
                "updated_at": project.updated_at.isoformat()
            }
            for project in projects
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/{project_id}")
def get_project(
    project_id: int,
    project_service: ProjectService = Depends(get_project_service)
) -> Dict[str, Any]:
    """
    Get a specific project by ID.
    
    Args:
        project_id: ID of the project to retrieve
        
    Returns:
        Project data
    """
    try:
        project = project_service.get_project(project_id)
        return {
            "id": project.id,
            "name": project.name,
            "created_at": project.created_at.isoformat(),
            "updated_at": project.updated_at.isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.put("/{project_id}")
def update_project(
    project_id: int,
    project_data: Dict[str, Any],
    project_service: ProjectService = Depends(get_project_service)
) -> Dict[str, Any]:
    """
    Update an existing project.
    
    Args:
        project_id: ID of the project to update
        project_data: Updated project data
        
    Returns:
        Updated project
    """
    try:
        # Filter out None values from the update data
        update_dict = {k: v for k, v in project_data.items() if v is not None}
        project = project_service.update_project(project_id, update_dict)
        return {
            "id": project.id,
            "name": project.name,
            "created_at": project.created_at.isoformat(),
            "updated_at": project.updated_at.isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.delete("/{project_id}")
def delete_project(
    project_id: int,
    project_service: ProjectService = Depends(get_project_service)
) -> Dict[str, str]:
    """
    Delete a project.
    
    Args:
        project_id: ID of the project to delete
        
    Returns:
        Confirmation message
    """
    try:
        result = project_service.delete_project(project_id)
        return {"message": result["message"]}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")