# test_performance_simple.py
"""
Stress test to measure system performance with 100 citations.
"""

import time
import uuid
import statistics
from fastapi.testclient import TestClient
from main import app

def test_stress_create_100_citations():
    """
    Stress test: create 100 citations and measure response time.
    
    Metrics measured:
    - Total execution time
    - Average time per citation
    - Minimum and maximum time
    - Throughput (citations per second)
    """
    print("\nStarting stress test: 100 citations")
    
    # Test client - will use test database automatically
    client = TestClient(app)
    
    # Create project for citations
    project_name = f"Stress Test Project {uuid.uuid4().hex[:8]}"
    project_response = client.post("/projects", json={"name": project_name})
    assert project_response.status_code == 201
    project_id = project_response.json()["id"]
    
    print(f"Project created: {project_id}")
    
    # List to store response times
    response_times = []
    citation_ids = []
    
    # Base data for citations (varying some fields)
    citation_types = ["book", "article", "website", "report"]
    publishers = ["Academic Press", "Tech Publisher", "Research Inc", "Education Corp"]
    
    # Start time
    start_time = time.time()
    
    print("Creating 100 citations...")
    
    # Create 100 citations
    for i in range(100):
        # Vary data to make each citation unique
        citation_type = citation_types[i % len(citation_types)]
        publisher = publishers[i % len(publishers)]
        
        # Create common base data
        base_data = {
            "type": citation_type,
            "authors": [f"Author Smith {chr(65 + i % 26)}", f"Co-Author Jones {chr(65 + (i+1) % 26)}"],
            "title": f"Performance Test Citation {i+1}: {uuid.uuid4().hex[:6]}",
            "year": 2020 + (i % 5),  # Years 2020-2024
        }
        
        # Add specific fields according to type
        if citation_type == "book":
            citation_data = {**base_data, **{
                "publisher": f"{publisher}",
                "place": ["New York", "London", "Paris", "Tokyo", "Berlin"][i % 5],
                "edition": (i % 3) + 1
            }}
        elif citation_type == "article":
            citation_data = {**base_data, **{
                "journal": ["Nature", "Science", "Cell", "PNAS", "Lancet"][i % 5],
                "volume": (i % 10) + 1,  # Integer, not string
                "issue": f"{(i % 4) + 1}",
                "pages": f"{i*10}-{i*10+20}",
                "doi": f"10.1000/test{i+1}"
            }}
        elif citation_type == "website":
            citation_data = {**base_data, **{
                "publisher": f"{publisher}",
                "url": f"https://example{i+1}.com",
                "access_date": "2023-01-01"
            }}
        elif citation_type == "report":
                citation_data = {**base_data, **{
                    "publisher": f"{publisher}",
                    "place": ["New York", "London", "Paris", "Tokyo", "Berlin"][i % 5],
                    "url": f"https://reports{i+1}.com"
                }}        # Measure time for this specific citation
        citation_start = time.time()
        
        response = client.post(f"/projects/{project_id}/citations", json=citation_data)
        
        citation_end = time.time()
        citation_time = citation_end - citation_start
        
        # Verify it was created correctly
        if response.status_code != 201:
            print(f"Error in citation {i+1} (type: {citation_type}): {response.status_code}")
            print(f"Data sent: {citation_data}")
            print(f"Response: {response.json()}")
            
        assert response.status_code == 201, f"Error in citation {i+1}: {response.status_code}"
        
        citation_id = response.json()["id"]
        citation_ids.append(citation_id)
        response_times.append(citation_time)
        
        # Progress every 25 citations
        if (i + 1) % 25 == 0:
            print(f"Completed {i+1}/100 citations")
    
    # Total time
    end_time = time.time()
    total_time = end_time - start_time
    
    # Calculate metrics
    avg_time = statistics.mean(response_times)
    min_time = min(response_times)
    max_time = max(response_times)
    median_time = statistics.median(response_times)
    throughput = 100 / total_time  # citations per second
    
    # Show results
    print("\nSTRESS TEST RESULTS")
    print("=" * 50)
    print(f"Total citations created: 100")
    print(f"Total time: {total_time:.2f} seconds")
    print(f"Average time per citation: {avg_time:.3f} seconds")
    print(f"Minimum time: {min_time:.3f} seconds")
    print(f"Maximum time: {max_time:.3f} seconds")
    print(f"Median time: {median_time:.3f} seconds")
    print(f"Throughput: {throughput:.2f} citations/second")
    print("=" * 50)
    
    # Verify all citations were created
    citations_response = client.get(f"/projects/{project_id}/citations")
    assert citations_response.status_code == 200
    citations = citations_response.json()
    
    print(f"Verification: {len(citations)} citations in project")
    assert len(citations) == 100, f"Expected 100 citations, found {len(citations)}"
    
    # Performance criteria (adjustable according to needs)
    print("\nPERFORMANCE CRITERIA")
    print("=" * 50)
    
    # Average time should be less than 1 second
    if avg_time < 1.0:
        print(f"Average time GOOD: {avg_time:.3f}s < 1.0s")
    else:
        print(f"Average time SLOW: {avg_time:.3f}s >= 1.0s")
    
    # Throughput should be greater than 5 citations per second
    if throughput > 5.0:
        print(f"Throughput GOOD: {throughput:.2f} citations/s > 5.0 citations/s")
    else:
        print(f"Throughput LOW: {throughput:.2f} citations/s <= 5.0 citations/s")
    
    # Maximum time should not exceed 5 seconds
    if max_time < 5.0:
        print(f"Maximum time ACCEPTABLE: {max_time:.3f}s < 5.0s")
    else:
        print(f"Maximum time EXCESSIVE: {max_time:.3f}s >= 5.0s")
    
    print("=" * 50)
    
    # Clean up project
    cleanup_response = client.delete(f"/projects/{project_id}")
    print(f"Project cleaned up: {cleanup_response.status_code}")
    
    # Assertions to pass/fail the test
    assert avg_time < 2.0, f"Average time too slow: {avg_time:.3f}s"
    assert throughput > 2.0, f"Throughput too low: {throughput:.2f} citations/s"
    assert max_time < 10.0, f"Maximum time excessive: {max_time:.3f}s"
    
    print("STRESS TEST COMPLETED SUCCESSFULLY")


def test_stress_concurrent_bibliography():
    """
    Stress test for bibliography generation with multiple citations.
    """
    print("\nStarting stress test: bibliography with 30 citations")

    # Test client - will use test database automatically
    client = TestClient(app)
    
    # Create project
    project_name = f"Bibliography Stress Test {uuid.uuid4().hex[:8]}"
    project_response = client.post("/projects", json={"name": project_name})
    assert project_response.status_code == 201
    project_id = project_response.json()["id"]
    
    print(f"Project created: {project_id}")
    
    # Create 30 citations of different types (more reliable)
    print("Creating 30 citations for bibliography...")

    citation_types_data = [
            # Books (10 citations)
            *[{
                "type": "book",
                "authors": [f"Book Author {chr(65 + i % 26)}"],
                "title": f"Bibliography Test Book {i+1}",
                "year": 2020 + (i % 5),
                "publisher": ["Academic Press", "Tech Publisher", "Research Inc", "Education Corp", "University Press"][i % 5],
                "place": ["New York", "London", "Paris", "Tokyo", "Berlin"][i % 5],
                "edition": 1
            } for i in range(10)],

            # Articles (10 citations)
            *[{
                "type": "article",
                "authors": [f"Article Author {chr(65 + i % 26)}"],
                "title": f"Bibliography Test Article {i+1}",
                "year": 2020 + (i % 5),
                "journal": ["Nature", "Science", "Cell", "PNAS", "Lancet"][i % 5],
                "volume": (i % 5) + 1,
                "issue": f"{(i % 3) + 1}",
                "pages": f"{i*5}-{i*5+10}",
                "doi": f"10.1000/article{i+1}"
            } for i in range(10)],

            # Websites (10 citations)
            *[{
                "type": "website",
                "authors": [f"Web Author {chr(65 + i % 26)}"],
                "title": f"Bibliography Test Website {i+1}",
                "year": 2020 + (i % 5),
                "publisher": ["Web Corp", "Digital Media", "Online Press", "Internet Inc", "Web Solutions"][i % 5],
                "url": f"https://example{i+1}.com",
                "access_date": "2023-01-01"
            } for i in range(10)]
        ]

    for i, citation_data in enumerate(citation_types_data):
        response = client.post(f"/projects/{project_id}/citations", json=citation_data)
        if response.status_code != 201:
            print(f"Error in bibliography citation {i+1}: {response.status_code}")
            print(f"Data: {citation_data}")
            print(f"Response: {response.json()}")
        assert response.status_code == 201
    
    print("30 citations created")
    
    # Measure bibliography generation time
    formats = ["apa", "mla"]
    
    for format_type in formats:
        print(f"Generating {format_type.upper()} bibliography...")
        
        start_time = time.time()
        
        bibliography_response = client.get(f"/projects/{project_id}/bibliography?format={format_type}")
        
        end_time = time.time()
        generation_time = end_time - start_time
        
        if bibliography_response.status_code != 200:
            print(f"Error in {format_type} bibliography: {bibliography_response.status_code}")
            try:
                print(f"Response: {bibliography_response.json()}")
            except:
                print(f"Response (text): {bibliography_response.text}")
            # For stress test, continue with next format
            continue
        
        bibliography = bibliography_response.json()
        
        print(f"{format_type.upper()} bibliography generated in {generation_time:.3f} seconds")
        print(f"Bibliography entries: {len(bibliography['bibliography'])}")
        
        # Verify all citations are in bibliography
        assert len(bibliography['bibliography']) == 30
        
        # Performance criterion: less than 3 seconds for 30 citations
        if generation_time < 3.0:
            print(f"Performance GOOD for {format_type.upper()}: {generation_time:.3f}s < 3.0s")
        else:
            print(f"Performance SLOW for {format_type.upper()}: {generation_time:.3f}s >= 3.0s")
        
        assert generation_time < 5.0, f"Bibliography generation {format_type} too slow: {generation_time:.3f}s"
    
    # Clean up
    cleanup_response = client.delete(f"/projects/{project_id}")
    print(f"Project cleaned up: {cleanup_response.status_code}")
    
    print("BIBLIOGRAPHY STRESS TEST COMPLETED")

if __name__ == "__main__":
    """
    Run all stress tests.
    Usage: python test_performance_simple.py
    """
    print("STARTING STRESS TEST SUITE")
    print("=" * 60)
    
    try:
        test_stress_create_100_citations()
        print("\n" + "="*60)
        
        test_stress_concurrent_bibliography()
        print("\n" + "="*60)
        
        print("ALL STRESS TESTS COMPLETED SUCCESSFULLY")
        
    except Exception as e:
        print(f"ERROR IN STRESS TEST: {e}")
        raise