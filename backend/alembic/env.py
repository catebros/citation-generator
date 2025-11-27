from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
from models.base import Base
# Import all models to ensure they're registered with Base.metadata
from models.citation import Citation
from models.project import Project
from models.project_citation import ProjectCitation
import os
from dotenv import load_dotenv

# Load environment variables - handle encoding issues on Windows
try:
    load_dotenv()
    DATABASE_URL = os.getenv("DATABASE_URL")
except:
    DATABASE_URL = None

# Fallback to a generic default (should be overridden by .env or environment variable)
if not DATABASE_URL:
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/citation_generator_db")

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
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
