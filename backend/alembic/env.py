import os

from alembic import context
from dotenv import load_dotenv
from models.base import Base

# Import all models to ensure they're registered with Base.metadata
from models.citation import Citation  # noqa: F401
from models.project import Project  # noqa: F401
from models.project_citation import ProjectCitation  # noqa: F401
from sqlalchemy import pool

# Load environment variables - handle encoding issues on Windows
try:
    load_dotenv()
    DATABASE_URL = os.getenv("DATABASE_URL")
except Exception:
    DATABASE_URL = None

# Fallback to a generic default
if not DATABASE_URL:
    default_url = "postgresql://postgres:postgres@localhost:5432/"
    default_url += "citation_generator_db"
    DATABASE_URL = os.getenv("DATABASE_URL", default_url)

config = context.config
# fileConfig disabled due to Windows path encoding issues
# fileConfig(config.config_file_name)
config.set_main_option("sqlalchemy.url", DATABASE_URL)
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    # Simplified to avoid config.get_section() encoding issues on Windows
    from sqlalchemy import create_engine

    connectable = create_engine(DATABASE_URL, poolclass=pool.NullPool)

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
