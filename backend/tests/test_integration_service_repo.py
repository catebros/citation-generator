# backend/tests/test_integration_service_repo.py
import pytest
from fastapi import HTTPException
from models.base import Base
from repositories.citation_repo import CitationRepository
from repositories.project_repo import ProjectRepository
from services.citation_service import CitationService
from services.project_service import ProjectService
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


@pytest.fixture(scope="function")
def db_session():
    """Create a fresh in-memory database for each test."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    yield session
    session.close()


@pytest.fixture
def citation_service(db_session):
    """Provide a CitationService instance with test database."""
    return CitationService(db_session)


@pytest.fixture
def project_service(db_session):
    """Provide a ProjectService instance with test database."""
    return ProjectService(db_session)


@pytest.fixture
def citation_repo(db_session):
    """Provide a CitationRepository instance with test database."""
    return CitationRepository(db_session)


@pytest.fixture
def project_repo(db_session):
    """Provide a ProjectRepository instance with test database."""
    return ProjectRepository(db_session)

def test_create_project_service_to_repo_integration(project_service, project_repo):
    """Test project creation flows from service through repository to database."""
    # Create project via service
    project_data = {"name": "Integration Test Project"}
    created_project = project_service.create_project(project_data)

    # Verify project exists in database via repository
    fetched_project = project_repo.get_by_id(created_project.id)

    assert fetched_project is not None
    assert fetched_project.id == created_project.id
    assert fetched_project.name == "Integration Test Project"
    assert fetched_project.created_at is not None


def test_update_project_service_to_repo_integration(project_service, project_repo):
    """Test project update flows from service through repository."""
    # Create project
    project = project_service.create_project({"name": "Original Name"})

    # Update via service
    updated_project = project_service.update_project(project.id, {"name": "Updated Name"})

    # Verify update persisted via repository
    fetched_project = project_repo.get_by_id(project.id)

    assert fetched_project.name == "Updated Name"
    assert updated_project.name == "Updated Name"


def test_delete_project_service_to_repo_integration(project_service, project_repo):
    """Test project deletion flows from service through repository."""
    # Create project
    project = project_service.create_project({"name": "To Delete"})
    project_id = project.id

    # Delete via service
    result = project_service.delete_project(project_id)

    # Verify deletion via repository
    fetched_project = project_repo.get_by_id(project_id)

    assert result == {"message": "Project deleted successfully"}
    assert fetched_project is None


def test_get_all_projects_service_to_repo_integration(project_service, project_repo):
    """Test retrieving all projects from service through repository."""
    # Create multiple projects via service
    project_service.create_project({"name": "Project 1"})
    project_service.create_project({"name": "Project 2"})
    project_service.create_project({"name": "Project 3"})

    # Get all via service
    all_projects = project_service.get_all_projects()

    # Verify via repository
    repo_projects = project_repo.get_all()

    assert len(all_projects) == 3
    assert len(repo_projects) == 3
    assert {p.name for p in all_projects} == {"Project 1", "Project 2", "Project 3"}


# ========== CITATION SERVICE + REPOSITORY INTEGRATION ==========


def test_create_citation_service_to_repo_integration(
    citation_service, project_service, citation_repo
):
    """Test citation creation flows from service through repository to database."""
    # Create project first
    project = project_service.create_project({"name": "Test Project"})

    # Create citation via service
    citation_data = {
        "type": "book",
        "title": "Test Book",
        "authors": ["Test Author"],
        "year": 2023,
        "publisher": "Test Publisher",
        "place": "New York",
        "edition": 1,
    }
    created_citation = citation_service.create_citation(project.id, citation_data)

    # Verify citation exists in database via repository
    fetched_citation = citation_repo.get_by_id(created_citation.id)

    assert fetched_citation is not None
    assert fetched_citation.id == created_citation.id
    assert fetched_citation.title == "Test Book"
    assert "Test Author" in fetched_citation.authors


def test_update_citation_service_to_repo_integration(
    citation_service, project_service, citation_repo
):
    """Test citation update flows from service through repository."""
    # Create project and citation
    project = project_service.create_project({"name": "Test Project"})
    citation_data = {
        "type": "book",
        "title": "Original Title",
        "authors": ["Author"],
        "year": 2023,
        "publisher": "Publisher",
        "place": "City",
        "edition": 1,
    }
    citation = citation_service.create_citation(project.id, citation_data)

    # Update via service
    update_data = {"title": "Updated Title", "year": 2024}
    updated_citation = citation_service.update_citation(
        citation.id, project.id, update_data
    )

    # Verify update persisted via repository
    fetched_citation = citation_repo.get_by_id(citation.id)

    assert fetched_citation.title == "Updated Title"
    assert fetched_citation.year == 2024
    assert updated_citation.title == "Updated Title"


def test_delete_citation_service_to_repo_integration(
    citation_service, project_service, citation_repo
):
    """Test citation deletion flows from service through repository."""
    # Create project and citation
    project = project_service.create_project({"name": "Test Project"})
    citation_data = {
        "type": "article",
        "title": "To Delete",
        "authors": ["Author"],
        "year": 2023,
        "journal": "Journal",
        "volume": 1,
        "issue": "1",
        "pages": "1-10",
        "doi": "10.1000/test",
    }
    citation = citation_service.create_citation(project.id, citation_data)
    citation_id = citation.id

    # Delete via service
    result = citation_service.delete_citation(citation_id, project.id)

    # Verify deletion via repository
    fetched_citation = citation_repo.get_by_id(citation_id)

    assert result == {"message": "Citation deleted"}
    assert fetched_citation is None


def test_get_citation_service_to_repo_integration(
    citation_service, project_service, citation_repo
):
    """Test retrieving citation from service through repository."""
    # Create project and citation
    project = project_service.create_project({"name": "Test Project"})
    citation_data = {
        "type": "website",
        "title": "Test Website",
        "authors": ["Web Author"],
        "year": 2023,
        "publisher": "Website Publisher",
        "url": "https://example.com",
        "access_date": "2023-01-01",
    }
    created_citation = citation_service.create_citation(project.id, citation_data)

    # Get via service
    fetched_citation = citation_service.get_citation(created_citation.id)

    # Verify via repository
    repo_citation = citation_repo.get_by_id(created_citation.id)

    assert fetched_citation.id == repo_citation.id
    assert fetched_citation.title == "Test Website"
    assert fetched_citation.url == "https://example.com"


# ========== CROSS-SERVICE INTEGRATION ==========


def test_project_citations_relationship_integration(
    project_service, citation_service, project_repo, citation_repo
):
    """Test that project-citation relationships work correctly across services."""
    # Create project
    project = project_service.create_project({"name": "Multi-Citation Project"})

    # Create multiple citations
    citation1_data = {
        "type": "book",
        "title": "Book 1",
        "authors": ["Author One"],
        "year": 2021,
        "publisher": "Publisher One",
        "place": "City One",
        "edition": 1,
    }
    citation2_data = {
        "type": "article",
        "title": "Article 1",
        "authors": ["Author Two"],
        "year": 2022,
        "journal": "Journal One",
        "volume": 5,
        "issue": "2",
        "pages": "10-20",
        "doi": "10.1000/test1",
    }

    citation1 = citation_service.create_citation(project.id, citation1_data)
    citation2 = citation_service.create_citation(project.id, citation2_data)

    # Get citations via project service
    project_citations = project_service.get_all_citations_by_project(project.id)

    # Verify via repository
    repo_citations = project_repo.get_all_by_project(project.id)

    assert len(project_citations) == 2
    assert len(repo_citations) == 2
    assert {c.id for c in project_citations} == {citation1.id, citation2.id}


def test_delete_project_cascades_citations_integration(
    project_service, citation_service, project_repo, citation_repo
):
    """Test that deleting a project properly handles citations (cascade or preserve)."""
    # Create project with unique citation
    project = project_service.create_project({"name": "Project to Delete"})
    citation_data = {
        "type": "book",
        "title": "Unique Book",
        "authors": ["Unique Author"],
        "year": 2023,
        "publisher": "Unique Publisher",
        "place": "Unique City",
        "edition": 1,
    }
    citation = citation_service.create_citation(project.id, citation_data)
    citation_id = citation.id

    # Delete project
    project_service.delete_project(project.id)

    # Verify project deleted
    fetched_project = project_repo.get_by_id(project.id)
    assert fetched_project is None

    # Citation should also be deleted (orphan cleanup)
    fetched_citation = citation_repo.get_by_id(citation_id)
    assert fetched_citation is None


def test_shared_citation_across_projects_integration(
    project_service, citation_service, citation_repo, db_session
):
    """Test that citations can be shared across multiple projects."""
    # Create two projects
    project1 = project_service.create_project({"name": "Project 1"})
    project2 = project_service.create_project({"name": "Project 2"})

    # Create same citation in both projects
    citation_data = {
        "type": "article",
        "title": "Shared Article",
        "authors": ["Shared Author"],
        "year": 2023,
        "journal": "Shared Journal",
        "volume": 10,
        "issue": "5",
        "pages": "100-200",
        "doi": "10.1000/shared",
    }

    citation1 = citation_service.create_citation(project1.id, citation_data)
    citation2 = citation_service.create_citation(project2.id, citation_data)

    # Should be same citation (deduplicated)
    assert citation1.id == citation2.id

    # Get citations for each project
    project1_citations = project_service.get_all_citations_by_project(project1.id)
    project2_citations = project_service.get_all_citations_by_project(project2.id)

    # Both should have the shared citation
    assert len(project1_citations) == 1
    assert len(project2_citations) == 1
    assert project1_citations[0].id == project2_citations[0].id


def test_update_shared_citation_creates_copy_integration(
    project_service, citation_service, citation_repo
):
    """Test that updating a shared citation creates a copy (copy-on-write)."""
    # Create two projects with shared citation
    project1 = project_service.create_project({"name": "Project Alpha"})
    project2 = project_service.create_project({"name": "Project Beta"})

    citation_data = {
        "type": "book",
        "title": "Shared Book",
        "authors": ["Shared Author"],
        "year": 2023,
        "publisher": "Shared Publisher",
        "place": "Shared City",
        "edition": 1,
    }

    citation1 = citation_service.create_citation(project1.id, citation_data)
    citation2 = citation_service.create_citation(project2.id, citation_data)

    original_id = citation1.id

    # Update citation in project1
    update_data = {"title": "Updated Book for Project 1"}
    updated_citation = citation_service.update_citation(
        citation1.id, project1.id, update_data
    )

    # Get citations for both projects
    project1_citations = project_service.get_all_citations_by_project(project1.id)
    project2_citations = project_service.get_all_citations_by_project(project2.id)

    # Project1 should have new citation with updated title
    assert len(project1_citations) == 1
    assert project1_citations[0].title == "Updated Book for Project 1"

    # Project2 should still have original citation
    assert len(project2_citations) == 1
    assert project2_citations[0].title == "Shared Book"
    assert project2_citations[0].id == original_id


def test_duplicate_detection_integration(citation_service, project_service):
    """Test duplicate citation detection across service and repository."""
    # Create project
    project = project_service.create_project({"name": "Duplicate Test Project"})

    # Create citation
    citation_data = {
        "type": "report",
        "title": "Test Report",
        "authors": ["Report Author"],
        "year": 2023,
        "publisher": "Report Publisher",
        "url": "https://example.com/report",
        "place": "Report City",
    }
    citation1 = citation_service.create_citation(project.id, citation_data)

    # Try to create duplicate
    with pytest.raises(HTTPException) as exc_info:
        citation_service.create_citation(project.id, citation_data)

    assert exc_info.value.status_code == 409
    assert "identical citation already exists" in exc_info.value.detail.lower()


def test_bibliography_generation_integration(
    project_service, citation_service, citation_repo
):
    """Test bibliography generation integrating service and repository layers."""
    # Create project
    project = project_service.create_project({"name": "Bibliography Test"})

    # Create multiple citations
    book_data = {
        "type": "book",
        "title": "Test Book for Bibliography",
        "authors": ["Book Author"],
        "year": 2023,
        "publisher": "Book Publisher",
        "place": "Book City",
        "edition": 2,
    }
    article_data = {
        "type": "article",
        "title": "Test Article for Bibliography",
        "authors": ["Article Author"],
        "year": 2023,
        "journal": "Test Journal",
        "volume": 15,
        "issue": "3",
        "pages": "50-75",
        "doi": "10.1000/bib",
    }

    citation_service.create_citation(project.id, book_data)
    citation_service.create_citation(project.id, article_data)

    # Generate bibliography via service
    bibliography_apa = project_service.generate_bibliography_by_project(
        project.id, format_type="apa"
    )
    bibliography_mla = project_service.generate_bibliography_by_project(
        project.id, format_type="mla"
    )

    # Verify both formats work
    assert bibliography_apa["citation_count"] == 2
    assert bibliography_mla["citation_count"] == 2
    assert len(bibliography_apa["bibliography"]) == 2
    assert len(bibliography_mla["bibliography"]) == 2

    # Verify different formatting
    assert bibliography_apa["bibliography"] != bibliography_mla["bibliography"]


def test_validation_errors_propagate_through_layers(citation_service, project_service):
    """Test that validation errors from repository propagate through service."""
    # Create project
    project = project_service.create_project({"name": "Validation Test"})

    # Try to create citation with missing required fields
    invalid_data = {
        "type": "book",
        "title": "Incomplete Book",
        "authors": ["Author"],
        # Missing: year, publisher, place, edition
    }

    with pytest.raises(HTTPException) as exc_info:
        citation_service.create_citation(project.id, invalid_data)

    assert exc_info.value.status_code == 400
    assert "required" in exc_info.value.detail.lower()


def test_transaction_rollback_on_error_integration(citation_service, project_service):
    """Test that database transactions rollback correctly on errors."""
    # Create project
    project = project_service.create_project({"name": "Transaction Test"})

    # Create valid citation
    valid_data = {
        "type": "book",
        "title": "Valid Book",
        "authors": ["Valid Author"],
        "year": 2023,
        "publisher": "Valid Publisher",
        "place": "Valid City",
        "edition": 1,
    }
    citation_service.create_citation(project.id, valid_data)

    # Try to create invalid citation (should fail)
    invalid_data = {"type": "unsupported_type", "title": "Invalid"}

    try:
        citation_service.create_citation(project.id, invalid_data)
    except HTTPException:
        pass

    # Verify only valid citation exists
    citations = project_service.get_all_citations_by_project(project.id)
    assert len(citations) == 1
    assert citations[0].title == "Valid Book"


def test_empty_project_integration(project_service, citation_service):
    """Test operations on project with no citations."""
    # Create empty project
    project = project_service.create_project({"name": "Empty Project"})

    # Get citations (should be empty)
    citations = project_service.get_all_citations_by_project(project.id)
    assert len(citations) == 0

    # Generate bibliography (should be empty)
    bibliography = project_service.generate_bibliography_by_project(
        project.id, format_type="apa"
    )
    assert bibliography["citation_count"] == 0
    assert len(bibliography["bibliography"]) == 0


def test_concurrent_citation_creation_integration(
    project_service, citation_service, citation_repo
):
    """Test creating multiple citations in sequence works correctly."""
    # Create project
    project = project_service.create_project({"name": "Concurrent Test"})

    # Create 5 different citations
    author_names = ["Author Alpha", "Author Beta", "Author Gamma", "Author Delta", "Author Epsilon"]
    for i in range(5):
        citation_data = {
            "type": "article",
            "title": f"Article {i}",
            "authors": [author_names[i]],
            "year": 2023,
            "journal": f"Journal {i}",
            "volume": i + 1,
            "issue": "1",
            "pages": f"{i * 10}-{i * 10 + 10}",
            "doi": f"10.1000/test{i}",
        }
        citation_service.create_citation(project.id, citation_data)

    # Verify all created
    citations = project_service.get_all_citations_by_project(project.id)
    assert len(citations) == 5

    # Verify all have unique IDs
    citation_ids = {c.id for c in citations}
    assert len(citation_ids) == 5


def test_project_name_uniqueness_integration(project_service, project_repo):
    """Test that project name uniqueness is enforced across layers."""
    # Create first project
    project_service.create_project({"name": "Unique Project Name"})

    # Try to create duplicate
    with pytest.raises(HTTPException) as exc_info:
        project_service.create_project({"name": "Unique Project Name"})

    assert exc_info.value.status_code == 409


def test_update_project_name_to_existing_integration(project_service):
    """Test that updating project name to existing name is prevented."""
    # Create two projects
    project1 = project_service.create_project({"name": "Project 1"})
    project_service.create_project({"name": "Project 2"})

    # Try to update project1 to have same name as project2
    with pytest.raises(HTTPException) as exc_info:
        project_service.update_project(project1.id, {"name": "Project 2"})

    assert exc_info.value.status_code == 409
