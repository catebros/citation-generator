# backend/tests/test_database.py
import pytest
from unittest.mock import patch, MagicMock
from sqlalchemy.orm import Session
from db.database import get_db, LocalSession, engine

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
    """Test that LocalSession creates valid sessions."""
    session = LocalSession()
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
    with patch('db.database.LocalSession') as mock_session_factory:
        mock_db = MagicMock()
        mock_session_factory.return_value = mock_db
        
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
    with patch('db.database.LocalSession') as mock_session_factory:
        mock_db = MagicMock()
        mock_session_factory.return_value = mock_db
        
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
    with patch('db.database.LocalSession') as mock_session_factory:
        # Mock LocalSession to raise exception during creation
        mock_session_factory.side_effect = Exception("Database connection failed")
        
        db_generator = get_db()
        
        # Should raise the exception from LocalSession creation
        with pytest.raises(Exception, match="Database connection failed"):
            next(db_generator)

@patch('db.database.LocalSession')
def test_get_db_generator_pattern(mock_local_session):
    """Test that get_db follows proper generator pattern."""
    mock_db = MagicMock()
    mock_local_session.return_value = mock_db
    
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