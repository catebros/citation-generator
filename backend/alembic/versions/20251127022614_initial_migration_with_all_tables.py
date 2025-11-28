"""Initial migration with all tables

Revision ID: 20251127022614
Revises:
Create Date: 2025-11-27T02:26:14.678316

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "20251127022614"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create citations table
    op.create_table(
        "citations",
        sa.Column("id", sa.Integer(), autoincrement="auto", nullable=False),
        sa.Column("type", sa.String(), nullable=False),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("authors", sa.Text(), nullable=False),
        sa.Column("year", sa.Integer(), nullable=True),
        sa.Column("publisher", sa.String(), nullable=True),
        sa.Column("journal", sa.String(), nullable=True),
        sa.Column("volume", sa.Integer(), nullable=True),
        sa.Column("issue", sa.String(), nullable=True),
        sa.Column("pages", sa.String(), nullable=True),
        sa.Column("doi", sa.String(), nullable=True),
        sa.Column("url", sa.String(), nullable=True),
        sa.Column("access_date", sa.String(), nullable=True),
        sa.Column("place", sa.String(), nullable=True),
        sa.Column("edition", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_citations_id"), "citations", ["id"], unique=False)

    # Create projects table
    op.create_table(
        "projects",
        sa.Column("id", sa.Integer(), autoincrement="auto", nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_projects_id"), "projects", ["id"], unique=False)

    # Create project_citations association table
    op.create_table(
        "project_citations",
        sa.Column("project_id", sa.Integer(), nullable=False),
        sa.Column("citation_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["citation_id"],
            ["citations.id"],
        ),
        sa.ForeignKeyConstraint(
            ["project_id"],
            ["projects.id"],
        ),
        sa.PrimaryKeyConstraint("project_id", "citation_id"),
    )


def downgrade() -> None:
    op.drop_table("project_citations")
    op.drop_index(op.f("ix_projects_id"), table_name="projects")
    op.drop_table("projects")
    op.drop_index(op.f("ix_citations_id"), table_name="citations")
    op.drop_table("citations")
