# backend/main.py
"""
Main FastAPI application for the Citation Generator API.
Provides endpoints for managing projects, citations, and bibliography formatting.
"""

from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

# Import database setup
from db.database import engine
from models.base import Base
from models.project import Project
from models.citation import Citation
from models.project_citation import ProjectCitation

# Import routers
from routers import projects, citations

# Create database tables
Base.metadata.create_all(bind=engine)

# Create FastAPI application
app = FastAPI(
    title="Citation Generator API",
    description="API for managing projects and generating bibliographic citations in APA and MLA formats",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS middleware for frontend connectivity
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact frontend domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(projects.router)
app.include_router(citations.router)

# Health check endpoints
@app.get("/", tags=["Health"])
def read_root():
    """Main health check endpoint."""
    return {
        "message": "Citation Generator API is running",
        "status": "healthy",
        "version": "1.0.0"
    }

@app.get("/health", tags=["Health"])
def health_check():
    """Detailed health check endpoint."""
    return {
        "status": "healthy",
        "database": "connected",
        "api_version": "1.0.0",
        "supported_formats": ["APA", "MLA"],
        "citation_types": ["article", "book", "website"]
    }

@app.get("/api/info", tags=["Info"])
def api_info():
    """
    API information and available endpoints.
    
    Returns:
        Detailed information about the API capabilities and endpoints
    """
    return {
        "api_name": "Citation Generator API",
        "version": "1.0.0",
        "description": "API for managing projects and generating bibliographic citations",
        "supported_formats": ["APA", "MLA"],
        "citation_types": ["article", "book", "website"],
        "endpoints": {
            "projects": {
                "create": "POST /projects",
                "list": "GET /projects",
                "get": "GET /projects/{id}",
                "update": "PUT /projects/{id}",
                "delete": "DELETE /projects/{id}"
            },
            "citations": {
                "create": "POST /projects/{project_id}/citations",
                "get": "GET /citations/{id}",
                "update": "PUT /projects/{project_id}/citations/{id}",
                "delete": "DELETE /projects/{project_id}/citations/{id}",
                "list_by_project": "GET /projects/{project_id}/citations"
            },
            "formatting": {
                "format_citation": "GET /citations/{id}/format?format_type={apa|mla}",
                "generate_bibliography": "GET /projects/{project_id}/bibliography?format_type={apa|mla}"
            }
        },
        "documentation": {
            "swagger_ui": "/docs",
            "redoc": "/redoc"
        }
    }

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler for unhandled errors."""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": f"Internal server error: {str(exc)}"}
    )

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="127.0.0.1", 
        port=8000,
        reload=True,
        log_level="info"
    )
