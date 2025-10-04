# backend/routers/citations.py
from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Dict, Any
import json
from dependencies import get_citation_service, get_project_service
from services.citation_service import CitationService
from services.project_service import ProjectService

router = APIRouter(tags=["Citations"])

@router.post("/projects/{project_id}/citations", status_code=status.HTTP_201_CREATED)
def create_citation(project_id: int, citation_data: Dict[str, Any], citation_service: CitationService = Depends(get_citation_service)) -> Dict[str, Any]:
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
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/citations/{citation_id}", status_code=status.HTTP_200_OK)
def get_citation(citation_id: int, citation_service: CitationService = Depends(get_citation_service)) -> Dict[str, Any]:
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
            "created_at": citation.created_at.isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.put("/projects/{project_id}/citations/{citation_id}", status_code=status.HTTP_200_OK)
def update_citation(project_id: int, citation_id: int, citation_data: Dict[str, Any], citation_service: CitationService = Depends(get_citation_service)) -> Dict[str, Any]:
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
        citation = citation_service.update_citation(citation_id, project_id, citation_data)
        
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
            "created_at": citation.created_at.isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.delete("/projects/{project_id}/citations/{citation_id}", status_code=status.HTTP_200_OK)
def delete_citation(project_id: int, citation_id: int, citation_service: CitationService = Depends(get_citation_service)) -> Dict[str, str]:
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
