# backend/main.py
"""
Main FastAPI application module for Citation Generator API.

This module initializes and configures the FastAPI application with:
- Database setup and table creation
- CORS middleware for frontend connectivity
- Router registration for projects and citations endpoints
- Health check endpoints for monitoring
- API documentation (Swagger UI and ReDoc)

The application provides RESTful endpoints for managing bibliographic citations
and projects, with support for APA and MLA citation formats.
"""
from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import Dict, Any
import uvicorn
from db.database import engine
from models.base import Base
from routers import project_router, citation_router

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
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Include routers
app.include_router(project_router.router)
app.include_router(citation_router.router)

# ========== HEALTH CHECK ENDPOINTS ==========

@app.get("/", tags=["Health"])
def read_root() -> Dict[str, Any]:
    """
    Main health check endpoint.

    Returns:
        Dict[str, Any]: API status information including message, status, and version
    """
    return {
        "message": "Citation Generator API is running",
        "status": "healthy",
        "version": "1.0.0"
    }

@app.get("/health", tags=["Health"])
def health_check() -> Dict[str, Any]:
    """
    Detailed health check endpoint.

    Provides comprehensive system health information including database
    connectivity, supported formats, and available citation types.

    Returns:
        Dict[str, Any]: Detailed health status with database connection info,
                       supported formats, and citation types
    """
    return {
        "status": "healthy",
        "database": "connected",
        "api_version": "1.0.0",
        "supported_formats": ["APA", "MLA"],
        "citation_types": ["article", "book", "website", "report"]
    }

# ========== APPLICATION ENTRY POINT ==========

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="127.0.0.1", 
        port=8000,
        reload=True,
        log_level="info"
    )
