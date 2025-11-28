# backend/schemas/project_schemas.py
from datetime import datetime

from pydantic import BaseModel, Field

# String length limits for validation
MAX_PROJECT_NAME_LENGTH = 200


class ProjectBase(BaseModel):
    """Base schema for project validation."""

    name: str = Field(
        ...,
        min_length=1,
        max_length=MAX_PROJECT_NAME_LENGTH,
        description="Project name",
    )


class ProjectCreate(ProjectBase):
    """Schema for creating a project."""

    pass


class ProjectUpdate(BaseModel):
    """Schema for updating a project with partial updates allowed."""

    name: str = Field(..., min_length=1, max_length=MAX_PROJECT_NAME_LENGTH)


class ProjectResponse(ProjectBase):
    """Schema for project responses."""

    id: int
    created_at: datetime

    class Config:
        from_attributes = True
