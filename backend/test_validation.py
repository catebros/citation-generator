#!/usr/bin/env python
"""Quick validation test to verify schemas work correctly."""

from schemas.citation_schemas import CitationCreate

# Test creating a valid citation
try:
    citation_data = {
        "type": "book",
        "authors": ["John Doe"],
        "title": "Test Book",
        "year": 2023,
        "publisher": "Test Publisher",
        "place": "New York",
        "edition": 1,
    }
    
    citation = CitationCreate(**citation_data)
    print("✅ Citation creation successful")
    print(f"   Type: {citation.type}")
    print(f"   Title: {citation.title}")
    print(f"   Authors: {citation.authors}")
    
except Exception as e:
    print(f"❌ Error: {type(e).__name__}: {e}")

# Test with invalid data
try:
    invalid_data = {
        "type": "book",
        "authors": ["John Doe"],
        "title": "Test Book",
        "year": 2023,
        # Missing required: publisher, place, edition
    }
    
    citation = CitationCreate(**invalid_data)
    print("❌ Should have failed validation")
    
except Exception as e:
    print(f"✅ Validation correctly rejected invalid data: {e}")
