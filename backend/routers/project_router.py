# backend/routers/project_router.py
import json
from typing import Any, Dict, List

from dependencies import get_project_service
from fastapi import APIRouter, Depends, HTTPException, Query, status
from services.project_service import ProjectService

router = APIRouter(tags=["Projects"])

@router.post("/projects", status_code=status.HTTP_201_CREATED)
def create_project(
    project_data: Dict[str, Any],
    project_service: ProjectService = Depends(get_project_service),
) -> Dict[str, Any]:
    """
    Create a new project.
    """
    try:
        project = project_service.create_project(project_data)
        return {
            "id": project.id,
            "name": project.name,
            "created_at": project.created_at.isoformat(),
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/projects", status_code=status.HTTP_200_OK)
def get_all_projects(
    project_service: ProjectService = Depends(get_project_service),
) -> List[Dict[str, Any]]:
    """
    Get all projects.
    """
    try:
        projects = project_service.get_all_projects()
        return [
            {
                "id": project.id,
                "name": project.name,
                "created_at": project.created_at.isoformat(),
            }
            for project in projects
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/projects/{project_id}", status_code=status.HTTP_200_OK)
def get_project(
    project_id: int, project_service: ProjectService = Depends(get_project_service)
) -> Dict[str, Any]:
    """
    Get a specific project by ID.
    """
    try:
        project = project_service.get_project(project_id)
        return {
            "id": project.id,
            "name": project.name,
            "created_at": project.created_at.isoformat(),
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.put("/projects/{project_id}", status_code=status.HTTP_200_OK)
def update_project(
    project_id: int,
    project_data: Dict[str, Any],
    project_service: ProjectService = Depends(get_project_service),
) -> Dict[str, Any]:
    """
    Update an existing project.
    """
    try:
        project = project_service.update_project(project_id, project_data)
        return {
            "id": project.id,
            "name": project.name,
            "created_at": project.created_at.isoformat(),
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.delete("/projects/{project_id}", status_code=status.HTTP_200_OK)
def delete_project(
    project_id: int, project_service: ProjectService = Depends(get_project_service)
) -> Dict[str, str]:
    """
    Delete a project.
    """
    try:
        return project_service.delete_project(project_id)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/projects/{project_id}/bibliography", status_code=status.HTTP_200_OK)
def generate_bibliography(
    project_id: int,
    format_type: str = Query("apa", description="Format type (apa, mla)"),
    project_service: ProjectService = Depends(get_project_service),
) -> Dict[str, Any]:
    """
    Generate a complete bibliography for a project.
    """
    try:
        bibliography = project_service.generate_bibliography_by_project(
            project_id, format_type
        )
        return bibliography
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/projects/{project_id}/citations", status_code=status.HTTP_200_OK)
def get_project_citations(
    project_id: int, project_service: ProjectService = Depends(get_project_service)
) -> List[Dict[str, Any]]:
    """
    Get all citations for a specific project.
    """
    try:
        citations = project_service.get_all_citations_by_project(project_id)

        result = []
        for citation in citations:
            # Parse authors from JSON string for response
            authors = (
                json.loads(citation.authors)
                if isinstance(citation.authors, str)
                else citation.authors
            )

            result.append(
                {
                    "id": citation.id,
                    "type": citation.type,
                    "title": citation.title,
                    "authors": authors,
                    "year": citation.year,
                    "journal": citation.journal,
                    "volume": citation.volume,
                    "issue": citation.issue,
                    "pages": citation.pages,
                    "doi": citation.doi,
                    "publisher": citation.publisher,
                    "place": citation.place,
                    "edition": citation.edition,
                    "url": citation.url,
                    "access_date": citation.access_date,
                    "created_at": citation.created_at.isoformat(),
                }
            )

        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
