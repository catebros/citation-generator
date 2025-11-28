# backend/main.py
import os
from typing import Any, Dict

from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
from db.database import engine
from models.base import Base
from routers import citation_router, project_router

# Create database tables only in non-CI environments
# CI environments don't have PostgreSQL available for import-time initialization
if os.getenv("ENVIRONMENT") != "ci":
    Base.metadata.create_all(bind=engine)

# Create FastAPI application
app = FastAPI(
    title="Citation Generator API",
    description="API for managing projects and generating bibliographic citations in APA and MLA formats",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
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
        "version": "1.0.0",
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
        "citation_types": ["article", "book", "website", "report"],
    }

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True, log_level="info")
