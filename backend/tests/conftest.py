"""
Test configuration for the citation generator application.

This module provides test fixtures with mocked database sessions.
- Unit tests use real SQLite in-memory databases
- Router/integration tests use mocked databases
- Service/formatter tests use mocked sessions as needed
"""

import os
import sys
import tempfile
from unittest.mock import MagicMock

import pytest
import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

# Add backend to path to ensure proper imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set PostgreSQL as default database for all tests
db_url = "postgresql://user:password@localhost:5432/citation_db"
os.environ["DATABASE_URL"] = db_url

# Patch create_engine for db.database module
# This prevents real DB connections in db.database module

_original_create_engine = sqlalchemy.create_engine
_mock_postgres_engine = MagicMock()
_mock_postgres_engine.url = "postgresql://user:password@localhost:5432/citation_db"
_mock_postgres_engine.dispose = MagicMock()


def _selective_create_engine(*args, **kwargs):
    """Create engine, mocking PostgreSQL URLs but allowing SQLite."""
    url_str = str(args[0]) if args else kwargs.get("url", "")
    if "postgresql" in str(url_str) or "psycopg" in str(url_str):
        # Return mock for PostgreSQL
        return _mock_postgres_engine
    else:
        # Return real engine for SQLite and other local DBs
        return _original_create_engine(*args, **kwargs)


# Patch create_engine module-wide before imports
sqlalchemy.create_engine = _selective_create_engine


@pytest.fixture
def mock_db_session():
    """
    Fixture providing a mocked SQLAlchemy Session for unit tests.
    This fixture does NOT connect to any real database.
    """
    session = MagicMock(spec=Session)

    # Mock query() to return a chainable object
    query_mock = MagicMock()
    session.query.return_value = query_mock

    # Add chainable methods for filtering
    query_mock.filter.return_value = query_mock
    query_mock.filter_by.return_value = query_mock
    query_mock.order_by.return_value = query_mock
    query_mock.all.return_value = []
    query_mock.first.return_value = None
    query_mock.one_or_none.return_value = None
    query_mock.count.return_value = 0

    # Mock add/commit/refresh
    session.add = MagicMock()
    session.commit = MagicMock()
    session.refresh = MagicMock()
    session.close = MagicMock()
    session.dispose = MagicMock()
    session.flush = MagicMock()
    session.execute = MagicMock()

    # Mock scalar operations
    scalar_mock = MagicMock()
    scalar_mock.first.return_value = None
    scalar_mock.one_or_none.return_value = None
    scalar_mock.all.return_value = []

    execute_result = MagicMock()
    execute_result.scalar.return_value = None
    execute_result.scalar_one_or_none.return_value = None
    execute_result.scalars.return_value = scalar_mock

    session.execute.return_value = execute_result

    yield session


@pytest.fixture
def mock_engine_fixture():
    """
    Fixture providing a mocked SQLAlchemy Engine for unit tests.
    This fixture does NOT create any real database connections.
    """
    engine = MagicMock()
    engine.url = "postgresql://user:password@localhost:5432/citation_db"
    engine.dispose = MagicMock()
    yield engine


@pytest.fixture(autouse=True)
def reset_database_engine():
    """
    Reset DatabaseEngine singleton state before/after each test to prevent cross-test contamination.
    """
    try:
        from db.database import DatabaseEngine

        if hasattr(DatabaseEngine, "reset_instance"):
            DatabaseEngine.reset_instance()
    except (ImportError, AttributeError):
        pass

    yield

    try:
        from db.database import DatabaseEngine

        if hasattr(DatabaseEngine, "reset_instance"):
            DatabaseEngine.reset_instance()
    except (ImportError, AttributeError):
        pass


@pytest.fixture
def mock_get_db(mock_db_session):
    """
    Fixture that patches get_db to return a mock session.
    Use in integration tests for database access without real DB.
    """
    from unittest.mock import patch

    with patch("db.database.get_db") as mock_get_db_func:

        def mock_get_db_gen():
            yield mock_db_session

        mock_get_db_func.return_value = mock_get_db_gen()
        yield mock_get_db_func


@pytest.fixture(autouse=True)
def auto_mock_get_db(request, mock_db_session):
    """
    Automatically patches get_db for non-integration tests.
    Integration tests that use TestClient are skipped.
    """
    from unittest.mock import patch

    # Skip mocking for integration tests that need real DB
    if (
        "integration" in request.node.name
        or "performance" in request.node.name
        or "main" in request.node.name
    ):
        # These tests need real DB setup instead
        yield
        return

    # For other tests, use mock
    def mock_get_db_gen():
        yield mock_db_session

    with patch("db.database.get_db", side_effect=lambda: mock_get_db_gen()):
        yield


@pytest.fixture(scope="function")
def integration_db_engine(request):
    """
    Create a fresh in-memory SQLite database for each integration test.
    Using in-memory database ensures complete isolation between tests.
    """
    # Use in-memory SQLite database
    # Each test gets completely isolated database that's automatically cleaned up
    db_url = "sqlite:///:memory:"

    engine = create_engine(
        db_url,
        connect_args={"check_same_thread": False},
        echo=False,
        poolclass=sqlalchemy.pool.StaticPool
    )

    # Import and create tables
    from models.base import Base

    Base.metadata.create_all(engine)

    yield engine

    # Cleanup
    Base.metadata.drop_all(engine)
    engine.dispose()


@pytest.fixture(autouse=True)
def setup_integration_db(request, integration_db_engine):
    """
    Setup SQLite database for integration tests.
    Each test gets its own fresh database.
    """
    # Only apply to integration/performance/main tests
    if not (
        "integration" in request.node.name
        or "performance" in request.node.name
        or "main" in request.node.name
    ):
        yield
        return

    # Use unique integration_db_engine for this test
    engine = integration_db_engine

    # Patch database.engine to use our test database
    from db import database

    original_engine = database.engine
    database.engine = engine

    TestSessionLocal = sessionmaker(bind=engine, expire_on_commit=False)

    def test_get_db():
        """Generator for test database sessions."""
        db = TestSessionLocal()
        try:
            yield db
        finally:
            db.close()

    # Patch db.database.get_db
    original_get_db_database = database.get_db
    database.get_db = test_get_db

    # Override in FastAPI app
    from main import app
    from db.database import get_db as db_get_db_ref

    app.dependency_overrides[db_get_db_ref] = test_get_db

    yield

    # Cleanup patches and overrides
    database.engine = original_engine
    database.get_db = original_get_db_database

    # Clear app dependency overrides
    app.dependency_overrides.clear()
