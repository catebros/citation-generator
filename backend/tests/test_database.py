# backend/tests/test_database.py
import pytest
from unittest.mock import patch, MagicMock
from sqlalchemy.orm import Session
from db.database import get_db, LocalSession, engine, DatabaseEngine

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

def test_engine_configuration():
    """Test that the database engine is properly configured."""
    assert engine is not None
    assert "sqlite" in str(engine.url)

def test_local_session_factory():
    """Test that session factory creates valid sessions."""
    from db.database import get_session_factory
    session_factory = get_session_factory()
    session = session_factory()
    assert isinstance(session, Session)
    session.close()

def test_get_db_returns_session(consume_generator):
    """Test that get_db yields a valid database session."""
    db_generator = get_db()
    db_session = next(db_generator)
    
    assert isinstance(db_session, Session)
    
    # Close the generator to trigger cleanup
    consume_generator(db_generator)

def test_get_db_closes_session_on_completion():
    """Test that database session is closed after generator completes."""
    with patch('db.database.get_session_factory') as mock_session_factory:
        mock_session_class = MagicMock()
        mock_db = MagicMock()
        mock_session_class.return_value = mock_db
        mock_session_factory.return_value = mock_session_class
        
        db_generator = get_db()
        db_session = next(db_generator)
        
        # Simulate completion of the generator
        try:
            next(db_generator)
        except StopIteration:
            pass
        
        # Verify close was called
        mock_db.close.assert_called_once()

def test_get_db_closes_session_on_exception():
    """Test that database session is closed even when exception occurs."""
    with patch('db.database.get_session_factory') as mock_session_factory:
        mock_session_class = MagicMock()
        mock_db = MagicMock()
        mock_session_class.return_value = mock_db
        mock_session_factory.return_value = mock_session_class
        
        db_generator = get_db()
        db_session = next(db_generator)
        
        # Simulate exception in generator
        try:
            db_generator.throw(Exception("Test exception"))
        except Exception:
            pass
        
        # Verify close was called despite exception
        mock_db.close.assert_called_once()

def test_get_db_handles_session_creation_failure():
    """Test that get_db properly handles LocalSession creation failure."""
    with patch('db.database.get_session_factory') as mock_session_factory:
        # Mock session factory to raise exception during creation
        mock_session_factory.side_effect = Exception("Database connection failed")
        
        db_generator = get_db()
        
        # Should raise the exception from session factory creation
        with pytest.raises(Exception, match="Database connection failed"):
            next(db_generator)

@patch('db.database.get_session_factory')
def test_get_db_generator_pattern(mock_session_factory):
    """Test that get_db follows proper generator pattern."""
    mock_session_class = MagicMock()
    mock_db = MagicMock()
    mock_session_class.return_value = mock_db
    mock_session_factory.return_value = mock_session_class
    
    generator = get_db()
    
    # Test it's a generator
    assert hasattr(generator, '__next__')
    assert hasattr(generator, '__iter__')
    
    # Test yielding
    yielded_session = next(generator)
    assert yielded_session == mock_db
    
    # Test cleanup on StopIteration
    with pytest.raises(StopIteration):
        next(generator)
    
    mock_db.close.assert_called_once()

def test_database_session_isolation(consume_generator):
    """Test that different calls to get_db return independent sessions."""
    gen1 = get_db()
    gen2 = get_db()
    
    session1 = next(gen1)
    session2 = next(gen2)
    
    # Sessions should be different objects
    assert session1 is not session2
    
    # Cleanup both generators
    consume_generator(gen1)
    consume_generator(gen2)

def test_database_engine_singleton_behavior():
    """Test that DatabaseEngine instances are the same object."""
    # Reset to ensure clean state
    DatabaseEngine.reset_instance()
    
    engine1 = DatabaseEngine()
    engine2 = DatabaseEngine()
    
    # Both instances should be the exact same object
    assert engine1 is engine2
    assert id(engine1) == id(engine2)

def test_reset_instance_creates_new_engine():
    """Test that reset_instance creates a new engine and disposes the old one."""
    # Reset to ensure clean state
    DatabaseEngine.reset_instance()
    
    # Create first engine instance
    db_engine1 = DatabaseEngine()
    engine1 = db_engine1.get_engine()
    
    # Patch the dispose method before calling reset_instance
    with patch.object(engine1, 'dispose') as mock_dispose:
        # Reset the instance
        DatabaseEngine.reset_instance()
        
        # dispose should have been called on the old engine
        mock_dispose.assert_called_once()
    
    # Create new engine instance
    db_engine2 = DatabaseEngine()
    engine2 = db_engine2.get_engine()
    
    # Engines should be different objects
    assert engine1 is not engine2
    assert id(engine1) != id(engine2)

def test_reset_instance_without_existing_engine():
    """Test that reset_instance works even when no engine exists."""
    # Reset to ensure clean state
    DatabaseEngine.reset_instance()
    
    # This should not raise any exceptions
    DatabaseEngine.reset_instance()
    
    # Should still be able to create a new instance
    db_engine = DatabaseEngine()
    engine = db_engine.get_engine()
    assert engine is not None

def test_local_session_uses_singleton_engine():
    """Test that LocalSession is using the singleton engine instance."""
    # Reset to ensure clean state
    DatabaseEngine.reset_instance()
    
    # Get the singleton engine
    singleton_engine = DatabaseEngine().get_engine()
    
    # Create a session using the session factory
    from db.database import get_session_factory
    session_factory = get_session_factory()
    session = session_factory()
    
    try:
        # The session's bind should be the same as our singleton engine
        assert session.bind is singleton_engine
        assert id(session.bind) == id(singleton_engine)
    finally:
        session.close()

def test_multiple_database_engines_share_same_engine():
    """Test that multiple DatabaseEngine instances share the same underlying engine."""
    # Reset to ensure clean state
    DatabaseEngine.reset_instance()
    
    # Create multiple DatabaseEngine instances
    db_engine1 = DatabaseEngine()
    db_engine2 = DatabaseEngine()
    db_engine3 = DatabaseEngine()
    
    # Get engines from each instance
    engine1 = db_engine1.get_engine()
    engine2 = db_engine2.get_engine()
    engine3 = db_engine3.get_engine()
    
    # All should be the same engine object
    assert engine1 is engine2 is engine3
    assert id(engine1) == id(engine2) == id(engine3)

def test_module_level_engine_uses_singleton():
    """Test that the module-level engine getter uses the singleton pattern."""
    # Reset to ensure clean state
    DatabaseEngine.reset_instance()
    
    # Get a fresh singleton engine
    singleton_engine = DatabaseEngine().get_engine()
    
    # The module-level engine getter should return the same as the singleton
    from db.database import get_singleton_engine
    module_engine = get_singleton_engine()
    
    # They should be the same instance
    assert singleton_engine is module_engine
    assert id(singleton_engine) == id(module_engine)