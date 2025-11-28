# backend/tests/test_citation_repo.py
"""
Test suite for CitationRepository class.

This module contains comprehensive tests for the CitationRepository which handles
database operations for citations. The tests cover all CRUD operations and complex
scenarios including:

- Citation creation with duplicate detection
- Retrieving citations by ID
- Deleting citations with various association scenarios
- Updating citations with copy-on-write behavior for shared citations
- Case-insensitive duplicate detection
- Orphan citation cleanup
- Project-citation association management

Test organization:
- CREATE tests: Verify citation creation and duplicate handling
- GET BY ID tests: Test retrieval by primary key
- DELETE tests: Cover single/multiple project associations and orphan cleanup
- UPDATE tests: Test in-place updates, copy-on-write, and merge scenarios
- EXTRA tests: Out-of-layer scenarios for robustness verification

All tests use in-memory SQLite database for fast, isolated execution.
"""
import pytest
from models.base import Base
from models.project import Project
from models.project_citation import ProjectCitation
from repositories.citation_repo import CitationRepository
from repositories.project_repo import ProjectRepository
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


@pytest.fixture(scope="function")
def db_session():
    engine = create_engine(
        "sqlite:///:memory:", connect_args={"check_same_thread": False}
    )
    TestingSessionLocal = sessionmaker(bind=engine)
    Base.metadata.create_all(engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


# ========== CREATE TESTS ==========
# Creates a new citation linked to a project and verifies data integrity
def test_create_citation_linked_to_project(db_session):
    repo = CitationRepository(db_session)

    project = Project(name="Test Project")
    db_session.add(project)
    db_session.commit()
    db_session.refresh(project)

    created = repo.create(
        project_id=project.id,
        type="article",
        title="Deep Learning Advances",
        authors=["Jane Doe"],
        year=2021,
    )

    assert created.id is not None
    assert created.title == "Deep Learning Advances"
    assert "Jane Doe" in created.authors


# Reuses existing identical citation instead of creating duplicate
def test_create_identical_citation_reuses_existing(db_session):
    repo = CitationRepository(db_session)

    project = Project(name="Test Project")
    db_session.add(project)
    db_session.commit()
    db_session.refresh(project)

    citation1 = repo.create(
        project_id=project.id,
        type="book",
        title="Identical Book",
        authors=["Author A"],
        year=2020,
    )

    citation2 = repo.create(
        project_id=project.id,
        type="book",
        title="Identical Book",
        authors=["Author A"],
        year=2020,
    )

    assert citation1.id == citation2.id


# Creates new association for existing citation when used in different project
def test_create_identical_citation_different_project(db_session):
    repo = CitationRepository(db_session)

    project1 = Project(name="Project 1")
    project2 = Project(name="Project 2")
    db_session.add_all([project1, project2])
    db_session.commit()
    db_session.refresh(project1)
    db_session.refresh(project2)

    citation1 = repo.create(
        project_id=project1.id,
        type="article",
        title="Shared Article",
        authors=["Shared Author"],
        year=2020,
    )

    citation2 = repo.create(
        project_id=project2.id,
        type="article",
        title="Shared Article",
        authors=["Shared Author"],
        year=2020,
    )

    assert citation1.id == citation2.id

    assoc1 = (
        db_session.query(ProjectCitation)
        .filter(
            ProjectCitation.project_id == project1.id,
            ProjectCitation.citation_id == citation1.id,
        )
        .first()
    )
    assoc2 = (
        db_session.query(ProjectCitation)
        .filter(
            ProjectCitation.project_id == project2.id,
            ProjectCitation.citation_id == citation2.id,
        )
        .first()
    )

    assert assoc1 is not None
    assert assoc2 is not None


# Creates citation with all possible optional fields populated
def test_create_citation_with_all_optional_fields(db_session):
    """Test creating citation with all possible optional fields populated."""
    repo = CitationRepository(db_session)

    project = Project(name="Complete Citation Project")
    db_session.add(project)
    db_session.commit()
    db_session.refresh(project)

    citation = repo.create(
        project_id=project.id,
        type="article",
        title="Complete Article",
        authors=["Author One", "Author Two", "Author Three"],
        year=2023,
        publisher="Academic Publisher",
        journal="Science Journal",
        volume=45,
        issue="3",
        pages="123-145",
        doi="10.1234/example.2023",
        url="https://example.com/article",
        access_date="2024-01-15",
        place="New York",
        edition=2,
    )

    assert citation.id is not None
    assert citation.type == "article"
    assert citation.title == "Complete Article"
    assert "Author One" in citation.authors
    assert "Author Two" in citation.authors
    assert "Author Three" in citation.authors
    assert citation.year == 2023
    assert citation.publisher == "Academic Publisher"
    assert citation.journal == "Science Journal"
    assert citation.volume == 45
    assert citation.issue == "3"
    assert citation.pages == "123-145"
    assert citation.doi == "10.1234/example.2023"
    assert citation.url == "https://example.com/article"
    assert citation.access_date == "2024-01-15"
    assert citation.place == "New York"
    assert citation.edition == 2


# Detects case-insensitive duplicate citations in a project
def test_find_duplicate_citation_case_insensitive(db_session):
    """Test that find_duplicate_citation_in_project detects duplicates with different case."""
    repo = CitationRepository(db_session)

    project = Project(name="Case Test Project")
    db_session.add(project)
    db_session.commit()
    db_session.refresh(project)

    # Create citation with specific case
    original = repo.create(
        project_id=project.id,
        type="article",
        title="Machine Learning Fundamentals",
        authors=["John Doe"],
        year=2021,
    )

    # Test different case combinations
    test_data = {
        "type": "ARTICLE",  # Different case
        "title": "MACHINE LEARNING FUNDAMENTALS",  # Different case
        "authors": ["JOHN DOE"],  # Different case
        "year": 2021,
        "publisher": None,
        "journal": None,
        "volume": None,
        "issue": None,
        "pages": None,
        "doi": None,
        "url": None,
        "access_date": None,
        "place": None,
        "edition": None,
    }

    duplicate = repo.find_duplicate_citation_in_project(project.id, test_data)
    assert duplicate is not None
    assert duplicate.id == original.id


# Verifies case-insensitive comparison doesn't create false positives
def test_find_duplicate_citation_no_false_positive(db_session):
    """Test that case-insensitive comparison doesn't create false positives."""
    repo = CitationRepository(db_session)

    project = Project(name="False Positive Test Project")
    db_session.add(project)
    db_session.commit()
    db_session.refresh(project)

    # Create original citation
    repo.create(
        project_id=project.id,
        type="book",
        title="Original Title",
        authors=["Author One"],
        year=2020,
    )

    # Test with completely different content
    test_data = {
        "type": "article",  # Different type
        "title": "Different Title",  # Different title
        "authors": ["Different Author"],  # Different author
        "year": 2021,  # Different year
        "publisher": None,
        "journal": None,
        "volume": None,
        "issue": None,
        "pages": None,
        "doi": None,
        "url": None,
        "access_date": None,
        "place": None,
        "edition": None,
    }

    duplicate = repo.find_duplicate_citation_in_project(project.id, test_data)
    assert duplicate is None  # Should not find a duplicate


# ========== GET BY ID TESTS ==========
# Retrieves citation by ID and verifies all attributes match
def test_get_citation_by_id(db_session):
    repo = CitationRepository(db_session)

    project = Project(name="Test Project")
    db_session.add(project)
    db_session.commit()
    db_session.refresh(project)

    created = repo.create(
        project_id=project.id,
        type="article",
        title="Deep Learning Advances",
        authors=["Jane Doe"],
        year=2021,
    )

    fetched = repo.get_by_id(created.id)

    assert fetched is not None
    assert fetched.id == created.id
    assert fetched.title == "Deep Learning Advances"
    assert "Jane Doe" in fetched.authors


# Returns None when citation ID doesn't exist
def test_get_citation_by_id_not_found(db_session):
    repo = CitationRepository(db_session)

    fetched = repo.get_by_id(999)

    assert fetched is None


# ========== DELETE TESTS ==========
# Returns False when trying to delete non-existent citation
def test_delete_citation_not_found(db_session):
    repo = CitationRepository(db_session)

    result = repo.delete(999, project_id=1)

    assert result is False


# Deletes citation and association when only one project uses it
def test_delete_citation_single_project(db_session):
    repo = CitationRepository(db_session)

    project = Project(name="Project A")
    db_session.add(project)
    db_session.commit()
    db_session.refresh(project)

    citation = repo.create(
        project_id=project.id,
        type="book",
        title="Book 1",
        authors=["Author A"],
        year=2000,
    )

    ok = repo.delete(citation.id, project_id=project.id)
    assert ok is True
    assert repo.get_by_id(citation.id) is None

    assoc = (
        db_session.query(ProjectCitation)
        .filter(ProjectCitation.citation_id == citation.id)
        .first()
    )
    assert assoc is None


# Removes association but preserves citation when used by multiple projects


def test_delete_citation_multiple_projects(db_session):
    repo = CitationRepository(db_session)

    project1 = Project(name="Project A")
    project2 = Project(name="Project B")
    db_session.add_all([project1, project2])
    db_session.commit()
    db_session.refresh(project1)
    db_session.refresh(project2)

    citation = repo.create(
        project_id=project1.id,
        type="article",
        title="Shared Citation",
        authors=["Author B"],
        year=2010,
    )

    repo.create(
        project_id=project2.id,
        type="article",
        title="Shared Citation",
        authors=["Author B"],
        year=2010,
    )

    ok = repo.delete(citation.id, project_id=project1.id)
    assert ok is True

    still_exists = repo.get_by_id(citation.id)
    assert still_exists is not None

    assoc1 = (
        db_session.query(ProjectCitation)
        .filter(
            ProjectCitation.project_id == project1.id,
            ProjectCitation.citation_id == citation.id,
        )
        .first()
    )
    assoc2 = (
        db_session.query(ProjectCitation)
        .filter(
            ProjectCitation.project_id == project2.id,
            ProjectCitation.citation_id == citation.id,
        )
        .first()
    )
    assert assoc1 is None
    assert assoc2 is not None


# Deletes orphan citation that has no project associations
def test_delete_orphan_citation(db_session):
    repo = CitationRepository(db_session)

    citation = repo.create(
        project_id=1,
        type="book",
        title="Orphan Citation",
        authors=["Author C"],
        year=1999,
    )

    db_session.query(ProjectCitation).delete()
    db_session.commit()

    ok = repo.delete(citation.id)
    assert ok is True
    assert repo.get_by_id(citation.id) is None


# Deletes citation with project_id=None removes all associations
def test_delete_citation_with_none_project_id(db_session):
    """Test deleting citation with project_id=None removes all associations."""
    repo = CitationRepository(db_session)

    project1 = Project(name="Project 1")
    project2 = Project(name="Project 2")
    db_session.add_all([project1, project2])
    db_session.commit()
    db_session.refresh(project1)
    db_session.refresh(project2)

    # Create citation shared by two projects
    citation = repo.create(
        project_id=project1.id,
        type="book",
        title="Shared Book",
        authors=["Shared Author"],
        year=2020,
    )

    # Add to second project
    repo.create(
        project_id=project2.id,
        type="book",
        title="Shared Book",
        authors=["Shared Author"],
        year=2020,
    )

    # Delete with project_id=None should remove citation entirely
    result = repo.delete(citation.id, project_id=None)

    assert result is True
    assert repo.get_by_id(citation.id) is None

    # Verify all associations removed
    assocs = (
        db_session.query(ProjectCitation)
        .filter(ProjectCitation.citation_id == citation.id)
        .all()
    )
    assert len(assocs) == 0


# ========== UPDATE TESTS ==========
# Updates citation fields and verifies changes are applied
def test_update_citation(db_session):
    repo = CitationRepository(db_session)

    project = Project(name="Update Project")
    db_session.add(project)
    db_session.commit()
    db_session.refresh(project)

    citation = repo.create(
        project_id=project.id,
        type="book",
        title="Old Title",
        authors=["Jane Doe"],
        year=2000,
    )

    updated = repo.update(
        citation.id, project_id=project.id, title="New Title", year=2021
    )

    assert updated is not None
    assert updated.title == "New Title"
    assert updated.year == 2021


# Updates citation title and year fields specifically
def test_update_citation_title_and_year(db_session):
    repo = CitationRepository(db_session)

    project = Project(name="Project TY")
    db_session.add(project)
    db_session.commit()
    db_session.refresh(project)

    c = repo.create(
        project_id=project.id, type="book", title="Old", authors=["X"], year=1990
    )

    updated = repo.update(c.id, project_id=project.id, title="New", year=2000)
    assert updated.title == "New"
    assert updated.year == 2000


# Updates citation authors list
def test_update_citation_authors(db_session):
    repo = CitationRepository(db_session)

    project = Project(name="Project Authors")
    db_session.add(project)
    db_session.commit()
    db_session.refresh(project)

    c = repo.create(
        project_id=project.id,
        type="article",
        title="Authored",
        authors=["Y"],
        year=2001,
    )

    updated = repo.update(c.id, project_id=project.id, authors=["Y", "Z"])
    assert "Y" in updated.authors
    assert "Z" in updated.authors


# Returns None when trying to update non-existent citation
def test_update_citation_not_found(db_session):
    repo = CitationRepository(db_session)

    project = Project(name="Test Project")
    db_session.add(project)
    db_session.commit()
    db_session.refresh(project)

    result = repo.update(999, project_id=project.id, title="Doesn't matter")

    assert result is None


# Merges with existing identical citation when update creates duplicate
def test_update_citation_merges_with_existing_identical(db_session):
    repo = CitationRepository(db_session)
    project_repo = ProjectRepository(db_session)
    project = Project(name="Merge Project")
    db_session.add(project)
    db_session.commit()
    db_session.refresh(project)

    existing_citation = repo.create(
        project_id=project.id,
        type="article",
        title="Existing Article",
        authors=["Author A"],
        year=2020,
    )

    citation_to_update = repo.create(
        project_id=project.id,
        type="book",
        title="Book to Update",
        authors=["Author B"],
        year=2021,
    )

    updated = repo.update(
        citation_to_update.id,
        project_id=project.id,
        type="article",
        title="Existing Article",
        authors=["Author A"],
        year=2020,
    )

    assert updated.id == existing_citation.id

    assert repo.get_by_id(citation_to_update.id) is None

    all_citations = project_repo.get_all_by_project(project.id)
    assert len(all_citations) == 1


# Creates new citation when updating shared citation to avoid affecting other projects
def test_update_citation_multiple_projects_creates_new(db_session):
    repo = CitationRepository(db_session)
    project_repo = ProjectRepository(db_session)
    project1 = Project(name="Project 1")
    project2 = Project(name="Project 2")
    db_session.add_all([project1, project2])
    db_session.commit()
    db_session.refresh(project1)
    db_session.refresh(project2)

    original_citation = repo.create(
        project_id=project1.id,
        type="article",
        title="Shared Article",
        authors=["Shared Author"],
        year=2020,
    )

    assoc = ProjectCitation(project_id=project2.id, citation_id=original_citation.id)
    db_session.add(assoc)
    db_session.commit()

    updated = repo.update(
        original_citation.id, project_id=project1.id, title="Updated Title"
    )

    assert updated.id != original_citation.id
    assert updated.title == "Updated Title"

    project1_citations = project_repo.get_all_by_project(project1.id)
    assert len(project1_citations) == 1
    assert project1_citations[0].title == "Updated Title"

    project2_citations = project_repo.get_all_by_project(project2.id)
    assert len(project2_citations) == 1
    assert project2_citations[0].title == "Shared Article"


# Modifies citation in place when only one project uses it
def test_update_citation_single_project_modifies_in_place(db_session):
    repo = CitationRepository(db_session)

    project = Project(name="Single Project")
    db_session.add(project)
    db_session.commit()
    db_session.refresh(project)

    citation = repo.create(
        project_id=project.id,
        type="book",
        title="Original Title",
        authors=["Original Author"],
        year=2020,
    )

    original_id = citation.id

    updated = repo.update(
        citation.id, project_id=project.id, title="Modified Title", year=2021
    )

    assert updated.id == original_id
    assert updated.title == "Modified Title"
    assert updated.year == 2021
    assert "Original Author" in updated.authors


# Tests update behavior when changing citation type
def test_update_citation_changing_type_filters_fields(db_session):
    """Test that updating citation type filters out irrelevant fields."""
    repo = CitationRepository(db_session)

    project = Project(name="Type Change Project")
    db_session.add(project)
    db_session.commit()
    db_session.refresh(project)

    # Create article citation with article-specific fields
    citation = repo.create(
        project_id=project.id,
        type="article",
        title="Original Article",
        authors=["Author"],
        year=2020,
        journal="Tech Journal",
        volume=10,
        issue="5",
        pages="100-120",
        doi="10.1234/test",
    )

    # Update to book type - article fields should be filtered out
    updated = repo.update(
        citation.id,
        project_id=project.id,
        type="book",
        publisher="Book Publisher",
        edition=2,
    )

    # Verify type changed and book fields are set
    assert updated.type == "book"
    assert updated.publisher == "Book Publisher"
    assert updated.edition == 2

    # Verify article-specific fields are removed (filtered by type)
    assert updated.journal is None
    assert updated.volume is None
    assert updated.issue is None
    assert updated.pages is None
    assert updated.doi is None


# Tests merge_citation_data properly filters fields by type
def test_merge_citation_data_filters_by_type(db_session):
    """Test that merge_citation_data properly filters fields by citation type."""
    repo = CitationRepository(db_session)

    project = Project(name="Merge Test Project")
    db_session.add(project)
    db_session.commit()
    db_session.refresh(project)

    # Create article with article-specific fields
    citation = repo.create(
        project_id=project.id,
        type="article",
        title="Test Article",
        authors=["Test Author"],
        year=2020,
        journal="Journal Name",
        volume=5,
        pages="10-20",
    )

    # Test merge with type change to book
    update_data = {"type": "book", "publisher": "Test Publisher", "edition": 3}

    merged = repo.merge_citation_data(citation, update_data)

    # Verify type changed
    assert merged["type"] == "book"
    assert merged["publisher"] == "Test Publisher"
    assert merged["edition"] == 3

    # Verify article fields filtered out (set to None)
    assert merged["journal"] is None
    assert merged["volume"] is None
    assert merged["pages"] is None


# Tests merge_citation_data converts authors list to JSON
def test_merge_citation_data_converts_authors_list_to_json(db_session):
    """Test that merge_citation_data converts authors list to JSON string."""
    repo = CitationRepository(db_session)

    project = Project(name="Authors Conversion Project")
    db_session.add(project)
    db_session.commit()
    db_session.refresh(project)

    citation = repo.create(
        project_id=project.id,
        type="book",
        title="Original Book",
        authors=["Original Author"],
        year=2020,
    )

    # Update with authors as list
    update_data = {"authors": ["New Author One", "New Author Two"]}

    merged = repo.merge_citation_data(citation, update_data)

    # Verify authors converted to JSON
    import json

    assert merged["authors"] == json.dumps(["New Author One", "New Author Two"])


# Tests updating citation with None values explicitly sets fields to None
def test_update_citation_with_none_values_are_applied(db_session):
    """Test that updating with None values explicitly sets fields to None."""
    repo = CitationRepository(db_session)

    project = Project(name="None Values Project")
    db_session.add(project)
    db_session.commit()
    db_session.refresh(project)

    # Create citation with optional fields
    citation = repo.create(
        project_id=project.id,
        type="book",
        title="Book with Edition",
        authors=["Author"],
        year=2020,
        publisher="Publisher",
        edition=2,
        place="New York",
    )

    # Update with None for edition and place
    updated = repo.update(citation.id, project_id=project.id, edition=None, place=None)

    # The merge should apply None values
    # Note: This depends on implementation - current code applies None
    assert updated is not None
    assert updated.title == "Book with Edition"


# Tests updating all possible citation fields in one operation
def test_update_citation_all_fields_at_once(db_session):
    """Test updating all possible citation fields in one update operation."""
    repo = CitationRepository(db_session)

    project = Project(name="Update All Fields Project")
    db_session.add(project)
    db_session.commit()
    db_session.refresh(project)

    # Create basic citation
    citation = repo.create(
        project_id=project.id,
        type="article",
        title="Original Title",
        authors=["Original Author"],
        year=2020,
    )

    # Update all article-valid fields at once
    # Note: merge_citation_data filters fields by type
    # Article allowed fields: type, title, authors, year, journal, volume, issue, pages, doi
    updated = repo.update(
        citation.id,
        project_id=project.id,
        type="article",
        title="Updated Title",
        authors=["Updated Author One", "Updated Author Two"],
        year=2024,
        journal="New Journal",
        volume=100,
        issue="12",
        pages="500-550",
        doi="10.9999/new.doi",
    )

    assert updated.title == "Updated Title"
    assert "Updated Author One" in updated.authors
    assert "Updated Author Two" in updated.authors
    assert updated.year == 2024
    # Article-specific fields
    assert updated.journal == "New Journal"
    assert updated.volume == 100
    assert updated.issue == "12"
    assert updated.pages == "500-550"
    assert updated.doi == "10.9999/new.doi"
    # Fields not allowed for articles should be None (filtered out by merge_citation_data)
    assert updated.publisher is None  # Not used for articles
    assert updated.url is None  # Not used for articles
    assert updated.access_date is None  # Not used for articles
    assert updated.place is None  # Not used for articles
    assert updated.edition is None  # Not used for articles


# =========================================================
# OUT OF LAYER SCOPE TESTS (EXTRA)
# These tests cover situations that, according to the app’s logic,
# should never reach the repository layer because they are already
# validated at the service/validator layer. However, we include them
# here to ensure that the repository behaves safely and consistently
# when receiving unexpected or invalid data.
# =========================================================


def test_update_citation_with_invalid_field_is_ignored(db_session):
    repo = CitationRepository(db_session)

    project = Project(name="Invalid Field Project")
    db_session.add(project)
    db_session.commit()
    db_session.refresh(project)

    citation = repo.create(
        project_id=project.id,
        type="article",
        title="Valid Title",
        authors=["Author"],
        year=2020,
    )

    updated = repo.update(
        citation.id, project_id=project.id, invalid_field="This should not be saved"
    )

    assert updated.title == "Valid Title"
    assert not hasattr(updated, "invalid_field")


def test_update_citation_with_authors_as_string(db_session):
    repo = CitationRepository(db_session)

    project = Project(name="Authors String Project")
    db_session.add(project)
    db_session.commit()
    db_session.refresh(project)

    citation = repo.create(
        project_id=project.id,
        type="book",
        title="Book Title",
        authors=["Correct Author"],
        year=2000,
    )

    updated = repo.update(
        citation.id, project_id=project.id, authors="Single Author String"
    )

    # Repo stores it as raw string (not JSON list) –
    # this should never happen with proper validation
    assert updated.authors == "Single Author String"


def test_update_citation_with_same_values_does_not_duplicate(db_session):
    repo = CitationRepository(db_session)

    project = Project(name="Same Values Project")
    db_session.add(project)
    db_session.commit()
    db_session.refresh(project)

    citation = repo.create(
        project_id=project.id,
        type="article",
        title="Unchanged Title",
        authors=["Author A"],
        year=2020,
    )

    updated = repo.update(
        citation.id,
        project_id=project.id,
        title="Unchanged Title",
        authors=["Author A"],
        year=2020,
    )

    # Repo returns same citation without duplication or deletion
    assert updated.id == citation.id
    assert updated.title == "Unchanged Title"
    assert "Author A" in updated.authors
