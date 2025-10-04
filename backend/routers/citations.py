# backend/routers/citations.py
"""
Citation-related API endpoints.
Handles CRUD operations for citations and formatting.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Dict, Any
import json
from dependencies import get_citation_service, get_project_service
from services.citation_service import CitationService
from services.project_service import ProjectService

router = APIRouter(tags=["Citations"])

@router.post("/projects/{project_id}/citations", status_code=status.HTTP_201_CREATED)
def create_citation(
    project_id: int,
    citation_data: Dict[str, Any],
    citation_service: CitationService = Depends(get_citation_service)
) -> Dict[str, Any]:
    """
    Create a new citation in a project.
    
    Args:
        project_id: ID of the project to associate the citation with
        citation_data: Citation creation data
        
    Returns:
        Created citation with assigned ID
    """
    try:
        citation = citation_service.create_citation(project_id, citation_data)
        
        # Parse authors from JSON string for response
        authors = json.loads(citation.authors) if isinstance(citation.authors, str) else citation.authors
        
        return {
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
            "updated_at": citation.updated_at.isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/citations/{citation_id}")
def get_citation(
    citation_id: int,
    citation_service: CitationService = Depends(get_citation_service)
) -> Dict[str, Any]:
    """
    Get a specific citation by ID.
    
    Args:
        citation_id: ID of the citation to retrieve
        
    Returns:
        Citation data
    """
    try:
        citation = citation_service.get_citation(citation_id)
        
        # Parse authors from JSON string for response
        authors = json.loads(citation.authors) if isinstance(citation.authors, str) else citation.authors
        
        return {
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
            "updated_at": citation.updated_at.isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.put("/projects/{project_id}/citations/{citation_id}")
def update_citation(
    project_id: int,
    citation_id: int,
    citation_data: Dict[str, Any],
    citation_service: CitationService = Depends(get_citation_service)
) -> Dict[str, Any]:
    """
    Update an existing citation.
    
    Args:
        project_id: ID of the associated project
        citation_id: ID of the citation to update
        citation_data: Updated citation data
        
    Returns:
        Updated citation
    """
    try:
        # Filter out None values from the update data
        update_dict = {k: v for k, v in citation_data.items() if v is not None}
        citation = citation_service.update_citation(citation_id, project_id, update_dict)
        
        # Parse authors from JSON string for response
        authors = json.loads(citation.authors) if isinstance(citation.authors, str) else citation.authors
        
        return {
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
            "updated_at": citation.updated_at.isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.delete("/projects/{project_id}/citations/{citation_id}")
def delete_citation(
    project_id: int,
    citation_id: int,
    citation_service: CitationService = Depends(get_citation_service)
) -> Dict[str, str]:
    """
    Delete a citation.
    
    Args:
        project_id: ID of the associated project
        citation_id: ID of the citation to delete
        
    Returns:
        Confirmation message
    """
    try:
        return citation_service.delete_citation(citation_id, project_id)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/projects/{project_id}/citations")
def get_project_citations(
    project_id: int,
    project_service: ProjectService = Depends(get_project_service)
) -> List[Dict[str, Any]]:
    """
    Get all citations for a specific project.
    
    Args:
        project_id: ID of the project
        
    Returns:
        List of citations belonging to the project
    """
    try:
        citations = project_service.get_all_citations_by_project(project_id)
        
        result = []
        for citation in citations:
            # Parse authors from JSON string for response
            authors = json.loads(citation.authors) if isinstance(citation.authors, str) else citation.authors
            
            result.append({
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
                "updated_at": citation.updated_at.isoformat()
            })
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/citations/{citation_id}/format")
def format_citation(
    citation_id: int,
    format_type: str = Query("apa", description="Format type (apa, mla)"),
    citation_service: CitationService = Depends(get_citation_service)
) -> Dict[str, Any]:
    """
    Format a citation in the specified style.
    
    Args:
        citation_id: ID of the citation to format
        format_type: Format type (apa, mla)
        
    Returns:
        Formatted citation in the requested style
    """
    try:
        # Get the citation
        citation = citation_service.get_citation(citation_id)
        
        # Format the citation
        formatted = citation_service.format_citation(citation, format_type)
        
        return {
            "citation_id": citation.id,
            "format_type": format_type.lower(),
            "formatted_citation": formatted
        }
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/projects/{project_id}/bibliography")
def generate_bibliography(
    project_id: int,
    format_type: str = Query("apa", description="Format type (apa, mla)"),
    project_service: ProjectService = Depends(get_project_service)
) -> Dict[str, Any]:
    """
    Generate a complete bibliography for a project.
    
    Args:
        project_id: ID of the project
        format_type: Format type (apa, mla)
        
    Returns:
        Complete formatted bibliography with all project citations
    """
    try:
        bibliography = project_service.generate_bibliography_by_project(project_id, format_type)
        return bibliography
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")