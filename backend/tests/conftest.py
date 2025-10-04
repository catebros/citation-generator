"""
Test configuration for the citation generator application.

This module provides test fixtures and configuration to ensure tests run
in isolation with a separate test database.
"""

import pytest
import os
from sqlalchemy import create_engine
from models.base import Base
from db.database import DatabaseEngine, TEST_DATABASE_URL

# Set pytest environment marker to ensure test database detection
os.environ["PYTEST_CURRENT_TEST"] = "true"


@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    """
    Set up test database for the entire test session.
    """
    # Reset the singleton to force reload with test detection
    DatabaseEngine.reset_instance()
    
    # Create test database tables
    test_engine = create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False}
    )
    Base.metadata.create_all(bind=test_engine)
    
    print(f"\n🧪 Test session using database: {TEST_DATABASE_URL}")
    
    yield
    
    # Cleanup after all tests
    test_engine.dispose()
    
    # Remove test database file if it exists (with error handling)
    try:
        if os.path.exists("test_citations.db"):
            # Give some time for connections to close
            import time
            time.sleep(0.1)
            os.remove("test_citations.db")
            print("🧹 Test database cleaned up")
    except PermissionError:
        # File might be in use, that's okay for testing
        print("⚠️  Test database file in use, will be cleaned up later")


@pytest.fixture(autouse=True)
def clean_database():
    """
    Clean the test database before each test.
    """
    # Get the test engine
    test_engine = create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False}
    )
    
    # Drop and recreate all tables for clean state
    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)
    
    # Reset singleton to pick up clean database
    DatabaseEngine.reset_instance()
    
    yield
    
    test_engine.dispose()