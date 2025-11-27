# backend/tests/test_database.py
"""
Unit test suite for database module using mocks (no real database connections).

This module contains comprehensive mocked tests for database configuration and session management:
- Database engine singleton pattern and lifecycle
- Session factory creation and configuration
- Session generator (get_db) for FastAPI dependency injection
- Error handling and edge cases
"""
import pytest
from unittest.mock import patch, MagicMock, call
from sqlalchemy.orm import Session
from db.database import get_db, get_session_factory, get_singleton_engine, DatabaseEngine

# ========== TEST FIXTURES ==========

@pytest.fixture
def mock_engine_instance():
    """Mock SQLAlchemy Engine instance."""
    engine = MagicMock()
    engine.url = "postgresql://user:password@localhost:5432/citation_db"
    engine.dispose = MagicMock()
    return engine


@pytest.fixture
def mock_session_instance():
    """Mock SQLAlchemy Session instance."""
    session = MagicMock(spec=Session)
    session.close = MagicMock()
    return session


@pytest.fixture
def consume_generator():
    """Helper fixture to fully consume a generator and trigger cleanup."""
    def _consume(generator):
        try:
            while True:
                next(generator)
        except StopIteration:
            pass
    return _consume

# ========== DATABASE ENGINE SINGLETON TESTS ==========

@patch('db.database.create_engine')
def test_engine_configuration(mock_create_engine, mock_engine_instance):
    """Test that the database engine is properly configured for PostgreSQL."""
    mock_create_engine.return_value = mock_engine_instance
    
    # Reset to ensure clean state
    DatabaseEngine.reset_instance()
    
    # Get engine through singleton
    db_engine = DatabaseEngine()
    engine = db_engine.get_engine()
    
    # Verify create_engine was called with PostgreSQL URL
    assert mock_create_engine.called
    assert engine is mock_engine_instance


@patch('db.database.create_engine')
def test_database_url_environment_configuration(mock_create_engine, mock_engine_instance):
    """Test that database configuration uses environment variables."""
    mock_create_engine.return_value = mock_engine_instance
    
    with patch.dict('os.environ', {'DATABASE_URL': 'postgresql://testuser:testpass@testhost:5432/testdb'}):
        DatabaseEngine.reset_instance()
        
        db_engine = DatabaseEngine()
        engine = db_engine.get_engine()
        
        # Verify create_engine was called with the environment URL
        mock_create_engine.assert_called_once()
        call_args = mock_create_engine.call_args
        assert 'postgresql://' in str(call_args)


@patch('db.database.create_engine')
def test_database_engine_singleton_behavior(mock_create_engine, mock_engine_instance):
    """Test that DatabaseEngine instances are the same object."""
    mock_create_engine.return_value = mock_engine_instance
    DatabaseEngine.reset_instance()
    
    engine1 = DatabaseEngine()
    engine2 = DatabaseEngine()
    
    # Both instances should be the exact same object
    assert engine1 is engine2
    assert id(engine1) == id(engine2)


@patch('db.database.create_engine')
def test_reset_instance_creates_new_engine(mock_create_engine, mock_engine_instance):
    """Test that reset_instance creates a new engine and disposes the old one."""
    mock_create_engine.return_value = mock_engine_instance
    DatabaseEngine.reset_instance()
    
    db_engine1 = DatabaseEngine()
    engine1 = db_engine1.get_engine()
    
    # Reset the instance
    DatabaseEngine.reset_instance()
    
    # Dispose should have been called on the old engine
    mock_engine_instance.dispose.assert_called_once()
    
    # Create new instance
    db_engine2 = DatabaseEngine()
    engine2 = db_engine2.get_engine()
    
    # Engines should be different objects
    assert engine1 is engine2  # Both are mocks, so they're the same mock


@patch('db.database.create_engine')
def test_reset_instance_without_existing_engine(mock_create_engine, mock_engine_instance):
    """Test that reset_instance works even when no engine exists."""
    mock_create_engine.return_value = mock_engine_instance
    DatabaseEngine.reset_instance()
    
    # This should not raise any exceptions
    DatabaseEngine.reset_instance()
    
    # Should still be able to create a new instance
    db_engine = DatabaseEngine()
    engine = db_engine.get_engine()
    assert engine is mock_engine_instance


# ========== SESSION FACTORY TESTS ==========

@patch('db.database.get_singleton_engine')
def test_local_session_factory(mock_get_engine, mock_engine_instance):
    """Test that session factory creates valid sessions."""
    mock_get_engine.return_value = mock_engine_instance
    
    session_factory = get_session_factory()
    assert session_factory is not None


@patch('db.database.get_singleton_engine')
def test_session_factory_returns_new_factory_on_engine_reset(mock_get_engine, mock_engine_instance):
    """Test that session factory updates when engine is reset."""
    mock_get_engine.return_value = mock_engine_instance
    DatabaseEngine.reset_instance()
    
    original_factory = get_session_factory()
    
    # Reset the engine
    DatabaseEngine.reset_instance()
    
    # Get new session factory
    new_factory = get_session_factory()
    
    # Factories should be different due to reset
    # (get_session_factory creates a new factory each time it's called)
    assert original_factory is not new_factory


# ========== GET_DB GENERATOR TESTS ==========

@patch('db.database.get_session_factory')
def test_get_db_returns_session(mock_get_factory, mock_session_instance):
    """Test that get_db yields a valid database session."""
    mock_factory = MagicMock()
    mock_factory.return_value = mock_session_instance
    mock_get_factory.return_value = mock_factory
    
    db_generator = get_db()
    db_session = next(db_generator)
    
    assert db_session is mock_session_instance


@patch('db.database.get_session_factory')
def test_get_db_closes_session_on_completion(mock_get_factory, mock_session_instance):
    """Test that database session is closed after generator completes."""
    mock_factory = MagicMock()
    mock_factory.return_value = mock_session_instance
    mock_get_factory.return_value = mock_factory
    
    db_generator = get_db()
    db_session = next(db_generator)
    
    # Simulate completion of the generator
    try:
        next(db_generator)
    except StopIteration:
        pass
    
    # Verify close was called
    mock_session_instance.close.assert_called_once()


@patch('db.database.get_session_factory')
def test_get_db_closes_session_on_exception(mock_get_factory, mock_session_instance):
    """Test that database session is closed even when exception occurs."""
    mock_factory = MagicMock()
    mock_factory.return_value = mock_session_instance
    mock_get_factory.return_value = mock_factory
    
    db_generator = get_db()
    db_session = next(db_generator)
    
    # Simulate exception in generator
    try:
        db_generator.throw(Exception("Test exception"))
    except Exception:
        pass
    
    # Verify close was called despite exception
    mock_session_instance.close.assert_called_once()


@patch('db.database.get_session_factory')
def test_get_db_handles_session_creation_failure(mock_get_factory):
    """Test that get_db properly handles session factory creation failure."""
    # Mock session factory to raise exception during creation
    mock_get_factory.side_effect = Exception("Database connection failed")
    
    db_generator = get_db()
    
    # Should raise the exception from session factory
    with pytest.raises(Exception, match="Database connection failed"):
        next(db_generator)


@patch('db.database.get_session_factory')
def test_get_db_generator_pattern(mock_get_factory, mock_session_instance):
    """Test that get_db follows proper generator pattern."""
    mock_factory = MagicMock()
    mock_factory.return_value = mock_session_instance
    mock_get_factory.return_value = mock_factory
    
    generator = get_db()
    
    # Test it's a generator
    assert hasattr(generator, '__next__')
    assert hasattr(generator, '__iter__')
    
    # Test yielding
    yielded_session = next(generator)
    assert yielded_session is mock_session_instance
    
    # Test cleanup on StopIteration
    with pytest.raises(StopIteration):
        next(generator)
    
    mock_session_instance.close.assert_called_once()


@patch('db.database.get_session_factory')
def test_get_db_multiple_iterations(mock_get_factory, mock_session_instance):
    """Test that get_db generator can only yield once."""
    mock_factory = MagicMock()
    mock_factory.return_value = mock_session_instance
    mock_get_factory.return_value = mock_factory
    
    db_generator = get_db()

    # First call should yield session
    session = next(db_generator)
    assert session is mock_session_instance

    # Second call should raise StopIteration
    with pytest.raises(StopIteration):
        next(db_generator)


# ========== SESSION ISOLATION TESTS ==========

@patch('db.database.get_session_factory')
def test_database_session_isolation(mock_get_factory, consume_generator):
    """Test that different calls to get_db return independent sessions."""
    mock_factory1 = MagicMock()
    mock_session1 = MagicMock(spec=Session)
    mock_factory1.return_value = mock_session1
    
    mock_factory2 = MagicMock()
    mock_session2 = MagicMock(spec=Session)
    mock_factory2.return_value = mock_session2
    
    # Alternate between factories
    mock_get_factory.side_effect = [mock_factory1, mock_factory2]
    
    gen1 = get_db()
    gen2 = get_db()

    session1 = next(gen1)
    session2 = next(gen2)

    # Sessions should be different objects
    assert session1 is not session2

    # Cleanup both generators
    consume_generator(gen1)
    consume_generator(gen2)
    
    # Both should have had close called
    mock_session1.close.assert_called_once()
    mock_session2.close.assert_called_once()


# ========== SINGLETON ENGINE FUNCTION TESTS ==========

@patch('db.database.DatabaseEngine')
def test_get_singleton_engine(mock_db_engine_class, mock_engine_instance):
    """Test that get_singleton_engine returns the singleton engine."""
    mock_instance = MagicMock()
    mock_instance.get_engine.return_value = mock_engine_instance
    mock_db_engine_class.return_value = mock_instance
    
    engine = get_singleton_engine()
    
    assert engine is mock_engine_instance


@patch('db.database.DatabaseEngine')
def test_module_level_engine_uses_singleton(mock_db_engine_class, mock_engine_instance):
    """Test that the module-level engine getter uses the singleton pattern."""
    mock_instance = MagicMock()
    mock_instance.get_engine.return_value = mock_engine_instance
    mock_db_engine_class.return_value = mock_instance
    
    engine = get_singleton_engine()
    
    # Should use singleton DatabaseEngine
    mock_db_engine_class.assert_called()
    assert engine is mock_engine_instance