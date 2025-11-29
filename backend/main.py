# backend/main.py
import os
from typing import Any, Dict

from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
from prometheus_fastapi_instrumentator import Instrumentator
from routers import citation_router, project_router

# Create database tables only in non-CI environments
# CI environments don't have PostgreSQL available for import-time initialization
if os.getenv("ENVIRONMENT") != "ci":
    from db.database import engine
    from models.base import Base
    try:
        Base.metadata.create_all(bind=engine)
    except Exception as e:
        # In CI or when database is not available, skip table creation
        # Tables will be created on first request or by migration scripts
        print(f"Skipping database table creation: {e}")

# Create FastAPI application
app = FastAPI(
    title="Citation Generator API",
    description="API for managing projects and generating bibliographic citations in APA and MLA formats",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure CORS middleware for frontend connectivity
# Uses ALLOWED_ORIGINS env var (comma-separated). Defaults to "*".
_raw_origins = os.getenv("ALLOWED_ORIGINS")
if _raw_origins:
    allowed_origins = [origin.strip() for origin in _raw_origins.split(",") if origin.strip()]
else:
    allowed_origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Setup Prometheus metrics
# This will expose metrics at /metrics endpoint
Instrumentator().instrument(app).expose(app)

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
    db_status = "connected"
    try:
        # Only check DB connection if not in CI environment
        if os.getenv("ENVIRONMENT") != "ci":
            from db.database import engine
            from sqlalchemy import text
            with engine.connect() as connection:
                connection.execute(text("SELECT 1"))
    except Exception as e:
        db_status = f"disconnected: {str(e)}"

    return {
        "status": "healthy" if db_status == "connected" else "degraded",
        "database": db_status,
        "api_version": "1.0.0",
        "supported_formats": ["APA", "MLA"],
        "citation_types": ["article", "book", "website", "report"],
    }

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True, log_level="info")
