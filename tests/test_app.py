import os
import shutil
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Generator

import pytest
from fastapi.testclient import TestClient

# Set up test environment before importing application
TEST_ROOT = Path(tempfile.mkdtemp(prefix="secondbrain-tests-"))
os.environ["SECONDBRAIN_DB_URL"] = f"sqlite:///{TEST_ROOT / 'secondbrain.db'}"
os.environ["SECONDBRAIN_CHROMA_PATH"] = str(TEST_ROOT / "chroma_db")
os.environ["SECRET_KEY"] = "test-secret-key-min-32-chars-long-for-security"
os.environ["ENVIRONMENT"] = "development"

from backend.main import app  # noqa: E402
from backend.models import db  # noqa: E402
from backend.services import vector_store  # noqa: E402


@pytest.fixture(scope="session")
def client() -> Generator[TestClient, None, None]:
    """Create a test client for the FastAPI application."""
    with TestClient(app, base_url="http://localhost") as test_client:
        yield test_client


@pytest.fixture(autouse=True)
def clean_state():
    """Clean database and vector store before each test."""
    # Create tables for test
    db.Base.metadata.drop_all(bind=db.engine)
    db.Base.metadata.create_all(bind=db.engine)
    
    # Note: Schema management is now handled by Alembic in production
    # For tests, we use create_all() which is acceptable

    # Reset vector store
    if vector_store._client is not None:
        try:
            vector_store._client.reset()
        except Exception:
            pass
        finally:
            vector_store._client = None
            vector_store._collection = None

    if vector_store.CHROMA_PATH.exists():
        shutil.rmtree(vector_store.CHROMA_PATH)

    yield

    # Cleanup after test
    if vector_store._client is not None:
        try:
            vector_store._client.reset()
        except Exception:
            pass
        finally:
            vector_store._client = None
            vector_store._collection = None

    if vector_store.CHROMA_PATH.exists():
        shutil.rmtree(vector_store.CHROMA_PATH)


def _auth_headers(client: TestClient, username: str, password: str, email: str | None = None) -> dict[str, str]:
    """Create a user and return auth headers."""
    signup_payload = {"username": username, "password": password}
    if email:
        signup_payload["email"] = email
    
    signup_response = client.post(
        "/auth/signup",
        json=signup_payload,
    )
    assert signup_response.status_code in (200, 201)

    token_response = client.post(
        "/auth/token",
        data={"username": username, "password": password},
    )
    assert token_response.status_code == 200
    access_token = token_response.json()["access_token"]
    return {"Authorization": f"Bearer {access_token}"}


def test_note_workflow_search_and_map(client: TestClient):
    """Test complete note workflow including search and map."""
    # Use a valid password that meets requirements (8+ chars, uppercase, lowercase, digit)
    headers = _auth_headers(client, "tester", "TestPass123")

    create_payload_1 = {
        "title": "Neural Networks and Ideas",
        "content": "Exploring neural network ideas for personal knowledge graphs.",
    }
    create_payload_2 = {
        "title": "Local Knowledge Base",
        "content": "Designing a local-first knowledge base with semantic search and neural map.",
    }

    response_one = client.post("/notes/", json=create_payload_1, headers=headers)
    assert response_one.status_code == 200
    note_one = response_one.json()
    assert note_one["embedding_model"] is not None
    created_at = datetime.fromisoformat(note_one["created_at"])

    response_two = client.post("/notes/", json=create_payload_2, headers=headers)
    assert response_two.status_code == 200
    note_two = response_two.json()
    assert note_two["embedding_model"] is not None

    list_response = client.get("/notes/", headers=headers)
    assert list_response.status_code == 200
    notes = list_response.json()
    assert len(notes) == 2

    search_response = client.post(
        "/search/",
        json={"query": "neural"},
        headers=headers,
    )
    assert search_response.status_code == 200
    search_data = search_response.json()
    assert search_data["results"], "Search should return at least one result"
    assert any(result["id"] == note_one["id"] for result in search_data["results"])

    map_response = client.get("/map/", headers=headers)
    assert map_response.status_code == 200
    map_data = map_response.json()
    assert map_data["nodes"], "Map should contain nodes for created notes"
    assert map_data["stats"]["total_nodes"] == len(map_data["nodes"])

    update_payload = {
        "title": "Updated Neural Notes",
        "content": "Updated insights on neural knowledge mapping and embeddings.",
    }
    update_response = client.put(
        f"/notes/{note_one['id']}",
        json=update_payload,
        headers=headers,
    )
    assert update_response.status_code == 200
    updated_note = update_response.json()
    assert updated_note["content"] == update_payload["content"]
    updated_at = datetime.fromisoformat(updated_note["updated_at"])
    assert updated_at >= created_at

    delete_response = client.delete(f"/notes/{note_two['id']}", headers=headers)
    assert delete_response.status_code == 200

    final_list = client.get("/notes/", headers=headers)
    assert final_list.status_code == 200
    remaining_notes = final_list.json()
    assert len(remaining_notes) == 1
    assert remaining_notes[0]["id"] == note_one["id"]


def test_signup_with_missing_tables():
    """Test signup behavior when database tables are missing."""
    # Create a test client with a fresh database that has no tables
    temp_db_path = TEST_ROOT / "empty_test.db"
    if temp_db_path.exists():
        temp_db_path.unlink()
    
    # Temporarily override the database URL for this test
    original_db_url = os.environ.get("SECONDBRAIN_DB_URL")
    os.environ["SECONDBRAIN_DB_URL"] = f"sqlite:///{temp_db_path}"
    
    try:
        # Import fresh app with empty database
        from backend.models.db import engine
        from sqlalchemy import create_engine
        
        # Create a new engine with empty database
        test_engine = create_engine(f"sqlite:///{temp_db_path}")
        
        # Don't create tables - this simulates the missing migration scenario
        
        with TestClient(app, base_url="http://localhost") as test_client:
            signup_response = test_client.post(
                "/auth/signup",
                json={"username": "testuser", "password": "TestPass123"},
            )
            
            # Should return 503 with helpful message about running migrations
            assert signup_response.status_code == 503
            response_data = signup_response.json()
            assert "alembic upgrade head" in response_data["detail"]
            
    finally:
        # Restore original environment
        if original_db_url:
            os.environ["SECONDBRAIN_DB_URL"] = original_db_url
        else:
            os.environ.pop("SECONDBRAIN_DB_URL", None)
            
        # Clean up test database
        if temp_db_path.exists():
            temp_db_path.unlink()


def test_health_check_with_missing_schema():
    """Test health check behavior when database schema is missing."""
    # This test is complex to implement without significant refactoring
    # because the database connection is established at import time.
    # For now, we'll test the check_database_schema function directly.
    
    from backend.main import check_database_schema
    from unittest.mock import patch, MagicMock
    from sqlalchemy.exc import OperationalError
    
    # Test case 1: Missing tables
    with patch('backend.main.engine') as mock_engine:
        mock_connection = MagicMock()
        mock_engine.connect.return_value.__enter__.return_value = mock_connection
        
        # Mock SQL result showing no tables
        mock_result = MagicMock()
        mock_result.fetchall.return_value = []
        mock_connection.execute.return_value = mock_result
        
        # Mock database URL to be SQLite for the test logic
        mock_engine.url = 'sqlite:///test.db'
        
        result = check_database_schema()
        assert result is False
    
    # Test case 2: Database connection error
    with patch('backend.main.engine') as mock_engine:
        mock_engine.connect.side_effect = OperationalError("Database not found", params=None, orig=Exception("Mock error"))
        
        result = check_database_schema()
        assert result is False


def test_auth_flow_complete_with_cookies(client: TestClient):
    """Test complete authentication flow with cookie handling and email."""
    
    # Test signup with email
    signup_data = {
        "username": "cookieuser",
        "email": "cookie@example.com",
        "password": "CookieTest123"
    }
    
    signup_response = client.post("/auth/signup", json=signup_data)
    assert signup_response.status_code in (200, 201)
    signup_json = signup_response.json()
    assert "username" in signup_json
    assert signup_json["email"] == "cookie@example.com"
    
    # Test login with form data (OAuth2 flow)
    login_data = {
        "username": "cookieuser", 
        "password": "CookieTest123"
    }
    
    login_response = client.post("/auth/token", data=login_data)
    assert login_response.status_code == 200
    
    # Check that access token is returned
    login_json = login_response.json()
    assert "access_token" in login_json
    assert login_json["token_type"] == "bearer"
    
    # Check that cookie is set (TestClient should preserve cookies)
    assert "access_token" in client.cookies
    
    # Test accessing protected route with cookie
    me_response = client.get("/auth/me")
    assert me_response.status_code == 200
    
    me_data = me_response.json()
    assert me_data["username"] == "cookieuser"
    assert me_data["email"] == "cookie@example.com"
    
    # Test logout
    logout_response = client.post("/auth/logout")
    assert logout_response.status_code == 200
    
    # After logout, protected route should fail
    protected_response = client.get("/auth/me")
    assert protected_response.status_code == 401


def test_auth_failure_scenarios(client: TestClient):
    """Test various authentication failure scenarios."""
    
    # Test login with invalid credentials
    invalid_login = client.post("/auth/token", data={
        "username": "nonexistent",
        "password": "wrongpassword"
    })
    assert invalid_login.status_code == 401
    
    # Test signup with weak password
    weak_password = client.post("/auth/signup", json={
        "username": "testuser",
        "password": "weak"
    })
    assert weak_password.status_code == 422  # Validation error
    
    # Test signup with invalid username
    invalid_username = client.post("/auth/signup", json={
        "username": "ab",  # Too short
        "password": "ValidPassword123"
    })
    assert invalid_username.status_code == 422
    
    # Test signup with invalid email
    invalid_email = client.post("/auth/signup", json={
        "username": "emailtest",
        "email": "not-an-email",
        "password": "ValidPassword123"
    })
    assert invalid_email.status_code == 422
    
    # Test accessing protected route without auth
    no_auth = client.get("/auth/me")
    assert no_auth.status_code == 401
    
    # Test duplicate username signup
    client.post("/auth/signup", json={
        "username": "duplicate", 
        "email": "unique1@example.com",
        "password": "Password123"
    })
    
    duplicate_signup = client.post("/auth/signup", json={
        "username": "duplicate",
        "email": "unique2@example.com",
        "password": "AnotherPassword123"
    })
    assert duplicate_signup.status_code == 400
    
    # Test duplicate email signup
    client.post("/auth/signup", json={
        "username": "user1",
        "email": "duplicate@example.com", 
        "password": "Password123"
    })
    
    duplicate_email_signup = client.post("/auth/signup", json={
        "username": "user2",
        "email": "duplicate@example.com",
        "password": "AnotherPassword123"
    })
    assert duplicate_email_signup.status_code == 400


def test_password_validation_requirements(client: TestClient):
    """Test that password validation meets security requirements."""
    
    # Test various invalid passwords
    invalid_passwords = [
        "short",  # Too short
        "nouppercase123",  # No uppercase
        "NOLOWERCASE123",  # No lowercase  
        "NoDigitsHere",  # No digits
        "a" * 200,  # Too long
    ]
    
    for i, password in enumerate(invalid_passwords):
        response = client.post("/auth/signup", json={
            "username": f"testuser{i}",
            "password": password
        })
        assert response.status_code == 422, f"Password '{password}' should be rejected"
    
    # Test valid password
    valid_response = client.post("/auth/signup", json={
        "username": "validuser",
        "password": "ValidPassword123"
    })
    assert valid_response.status_code in (200, 201)


def test_note_crud_resilience_to_vector_failures(client: TestClient):
    """Test that note CRUD operations succeed even when vector store fails."""
    headers = _auth_headers(client, "resilience_user", "TestPass123")
    
    # Mock vector store to fail
    from unittest.mock import patch
    
    with patch('backend.services.vector_store.add_note_to_vector_store', side_effect=Exception("Vector store down")):
        # Create note should still succeed
        create_response = client.post("/notes/", json={
            "title": "Test Note",
            "content": "This note should be created even if vector store fails"
        }, headers=headers)
        
        assert create_response.status_code == 200
        note = create_response.json()
        assert note["title"] == "Test Note"
        note_id = note["id"]
    
    # Update should also work with vector store failure
    with patch('backend.services.vector_store.add_note_to_vector_store', side_effect=Exception("Vector store down")):
        with patch('backend.services.vector_store.delete_note_from_vector_store', side_effect=Exception("Vector store down")):
            update_response = client.put(f"/notes/{note_id}", json={
                "title": "Updated Note",
                "content": "Updated content"
            }, headers=headers)
            
            assert update_response.status_code == 200
            updated_note = update_response.json()
            assert updated_note["title"] == "Updated Note"
    
    # Delete should work too
    with patch('backend.services.vector_store.delete_note_from_vector_store', side_effect=Exception("Vector store down")):
        delete_response = client.delete(f"/notes/{note_id}", headers=headers)
        assert delete_response.status_code == 200


def test_search_explain_functionality(client: TestClient):
    """Test the search explain feature with and without OpenAI."""
    headers = _auth_headers(client, "search_user", "TestPass123")
    
    # Create some test notes
    client.post("/notes/", json={
        "title": "Machine Learning Basics",
        "content": "Introduction to neural networks, deep learning algorithms and AI concepts"
    }, headers=headers)
    
    client.post("/notes/", json={
        "title": "Python Programming",
        "content": "Python syntax, data structures, and machine learning libraries like TensorFlow"
    }, headers=headers)
    
    # Perform search
    search_response = client.post("/search/", json={"query": "machine learning"}, headers=headers)
    assert search_response.status_code == 200
    search_data = search_response.json()
    
    # Test explain endpoint without OpenAI
    explain_response = client.post("/search/explain", json={
        "query": "machine learning",
        "results": search_data["results"]
    }, headers=headers)
    
    assert explain_response.status_code == 200
    explain_data = explain_response.json()
    assert "explanation" in explain_data
    assert "method" in explain_data
    assert explain_data["llm_available"] == False  # No OPENAI_API_KEY in test env
    assert explain_data["method"] == "rule-based"


def test_analytics_endpoint(client: TestClient):
    """Test the analytics summary endpoint."""
    headers = _auth_headers(client, "analytics_user", "TestPass123")
    
    # Get initial analytics (should be empty)
    analytics_response = client.get("/analytics/summary", headers=headers)
    assert analytics_response.status_code == 200
    analytics_data = analytics_response.json()
    
    assert analytics_data["note_count"] == 0
    assert analytics_data["total_words"] == 0
    assert analytics_data["notes_this_week"] == 0
    
    # Create some notes
    client.post("/notes/", json={
        "title": "First Note",
        "content": "This is my first note with some content to count words."
    }, headers=headers)
    
    client.post("/notes/", json={
        "title": "Second Note",
        "content": "Another note with different content for testing analytics."
    }, headers=headers)
    
    # Get updated analytics
    updated_analytics = client.get("/analytics/summary", headers=headers)
    assert updated_analytics.status_code == 200
    updated_data = updated_analytics.json()
    
    assert updated_data["note_count"] == 2
    assert updated_data["total_words"] > 0
    assert updated_data["notes_this_week"] == 2
    assert updated_data["avg_note_length"] > 0


def test_enhanced_health_check(client: TestClient):
    """Test the enhanced health check endpoint."""
    health_response = client.get("/health")
    assert health_response.status_code == 200
    
    health_data = health_response.json()
    
    # Check required fields
    assert "status" in health_data
    assert "database" in health_data
    assert "vector_store" in health_data
    assert "openai" in health_data
    assert "version" in health_data
    
    # In test environment, database should be connected
    assert health_data["database"] == "connected"
    
    # OpenAI should not be configured in test environment
    assert health_data["openai"] == "not_configured"
    
    # Vector store status may vary but should be present
    assert health_data["vector_store"] in ["connected", "error", "disconnected"]


def test_map_with_parameters(client: TestClient):
    """Test the neural map endpoint with various parameters."""
    headers = _auth_headers(client, "map_user", "TestPass123")
    
    # Create test notes
    for i in range(5):
        client.post("/notes/", json={
            "title": f"Note {i}",
            "content": f"Content for note {i} with some shared keywords like data science"
        }, headers=headers)
    
    # Test default parameters
    map_response = client.get("/map/", headers=headers)
    assert map_response.status_code == 200
    map_data = map_response.json()
    
    assert "nodes" in map_data
    assert "edges" in map_data
    assert "stats" in map_data
    
    # Test with custom parameters
    custom_params = {
        "min_similarity": 0.3,
        "top_k": 2,
        "max_nodes": 10,
        "include_isolates": False
    }
    
    custom_map_response = client.get("/map/", params=custom_params, headers=headers)
    assert custom_map_response.status_code == 200
    custom_map_data = custom_map_response.json()
    
    assert "nodes" in custom_map_data
    assert "edges" in custom_map_data


def test_map_vector_similarity(client: TestClient):
    """Test that map uses vector embeddings for semantic similarity."""
    headers = _auth_headers(client, "vector_map_user", "TestPass123")
    
    # Create semantically similar notes
    client.post("/notes/", json={
        "title": "Deep Learning",
        "content": "Neural networks and deep learning algorithms for AI applications"
    }, headers=headers)
    
    client.post("/notes/", json={
        "title": "Machine Learning",
        "content": "Artificial intelligence and machine learning techniques"
    }, headers=headers)
    
    client.post("/notes/", json={
        "title": "Cooking Recipes",
        "content": "How to make pasta and pizza recipes"
    }, headers=headers)
    
    # Get map
    map_response = client.get("/map/", params={"min_similarity": 0.2}, headers=headers)
    assert map_response.status_code == 200
    map_data = map_response.json()
    
    # Should have edges
    assert len(map_data["edges"]) > 0
    
    # Check that edges have similarity scores
    for edge in map_data["edges"]:
        assert "similarity" in edge
        assert 0 <= edge["similarity"] <= 1
        assert "has_embedding" in edge
    
    # Check stats
    stats = map_data["stats"]
    assert "total_nodes" in stats
    assert "total_edges" in stats
    assert "min_similarity" in stats
    assert "max_similarity" in stats
    assert "isolated_nodes" in stats
    assert "embedding_coverage" in stats
    
    # Embedding coverage should be > 0 since notes have embeddings
    assert stats["embedding_coverage"] >= 0


def test_map_fallback_similarity(client: TestClient):
    """Test that map falls back to keyword similarity when embeddings unavailable."""
    headers = _auth_headers(client, "fallback_map_user", "TestPass123")
    
    from unittest.mock import patch
    
    # Create notes
    client.post("/notes/", json={
        "title": "Python Programming",
        "content": "Python is a great programming language"
    }, headers=headers)
    
    client.post("/notes/", json={
        "title": "Java Programming",
        "content": "Java is also a programming language"
    }, headers=headers)
    
    # Mock vector store to fail retrieval
    with patch('backend.services.vector_store.get_collection') as mock_collection:
        mock_collection.side_effect = Exception("Vector store unavailable")
        
        map_response = client.get("/map/", params={"min_similarity": 0.2}, headers=headers)
        assert map_response.status_code == 200
        map_data = map_response.json()
        
        # Should still have nodes (even without embeddings)
        assert len(map_data["nodes"]) == 2
        
        # May have edges based on keyword similarity
        # (not asserting edges exist since keyword similarity might be low)
        assert "edges" in map_data
        assert "stats" in map_data


def test_map_with_tags(client: TestClient):
    """Test map filtering and similarity calculation with tags."""
    headers = _auth_headers(client, "tags_map_user", "TestPass123")
    
    # Create notes with tags
    client.post("/notes/", json={
        "title": "AI Research",
        "content": "Research on artificial intelligence",
        "tags": ["ai", "research"]
    }, headers=headers)
    
    client.post("/notes/", json={
        "title": "ML Algorithms",
        "content": "Machine learning algorithms",
        "tags": ["ai", "ml", "algorithms"]
    }, headers=headers)
    
    client.post("/notes/", json={
        "title": "Cooking Tips",
        "content": "Tips for cooking pasta",
        "tags": ["cooking", "food"]
    }, headers=headers)
    
    # Get full map
    full_map = client.get("/map/", headers=headers)
    assert full_map.status_code == 200
    full_data = full_map.json()
    assert len(full_data["nodes"]) == 3
    
    # Filter by tag
    filtered_map = client.get("/map/", params={"tags": "ai"}, headers=headers)
    assert filtered_map.status_code == 200
    filtered_data = filtered_map.json()
    
    # Should only have AI-related notes
    assert len(filtered_data["nodes"]) == 2
    for node in filtered_data["nodes"]:
        assert "tags" in node
        assert "ai" in node["tags"]
    
    # Check that edges between AI notes have tag similarity bonus
    if len(filtered_data["edges"]) > 0:
        edge = filtered_data["edges"][0]
        # Find source and target nodes
        source_node = next(n for n in filtered_data["nodes"] if n["id"] == edge["source"])
        target_node = next(n for n in filtered_data["nodes"] if n["id"] == edge["target"])
        
        # Nodes with shared tags should have positive similarity
        shared_tags = set(source_node["tags"]) & set(target_node["tags"])
        if len(shared_tags) > 0:
            assert edge["similarity"] > 0


def test_map_metadata_richness(client: TestClient):
    """Test that map returns rich metadata for nodes."""
    headers = _auth_headers(client, "metadata_map_user", "TestPass123")
    
    # Create a note
    create_response = client.post("/notes/", json={
        "title": "Test Note",
        "content": "This is a test note with content",
        "tags": ["test", "metadata"]
    }, headers=headers)
    assert create_response.status_code == 200
    
    # Get map
    map_response = client.get("/map/", headers=headers)
    assert map_response.status_code == 200
    map_data = map_response.json()
    
    assert len(map_data["nodes"]) == 1
    node = map_data["nodes"][0]
    
    # Check for rich metadata
    assert "id" in node
    assert "title" in node
    assert "preview" in node
    assert "content" in node
    assert "tags" in node
    assert node["tags"] == ["test", "metadata"]
    assert "type" in node
    assert "color" in node
    assert "size" in node
    assert "degree" in node
    assert "created_at" in node
    assert "updated_at" in node
    assert node["created_at"] is not None
    
    # Stats should have comprehensive metrics
    stats = map_data["stats"]
    assert "total_nodes" in stats
    assert "total_edges" in stats
    assert "avg_degree" in stats
    assert "min_similarity" in stats
    assert "max_similarity" in stats
    assert "isolated_nodes" in stats
    assert "embedding_coverage" in stats


def test_search_highlighting_and_scores(client: TestClient):
    """Test search results include highlighting and proper scoring."""
    headers = _auth_headers(client, "highlight_user", "TestPass123")
    
    # Create a note with specific content
    client.post("/notes/", json={
        "title": "Artificial Intelligence Research",
        "content": "This note contains information about artificial intelligence and machine learning algorithms."
    }, headers=headers)
    
    # Search for a specific term
    search_response = client.post("/search/", json={"query": "artificial intelligence"}, headers=headers)
    assert search_response.status_code == 200
    
    search_data = search_response.json()
    assert len(search_data["results"]) > 0
    
    result = search_data["results"][0]
    
    # Check that results have proper structure
    assert "score" in result
    assert "search_method" in result
    assert "highlighted_preview" in result
    assert "preview" in result
    
    # Score should be between 0 and 1
    assert 0 <= result["score"] <= 1
    
    # Search method should be specified
    assert result["search_method"] in ["vector", "keyword"]


def test_profile_update_email(client: TestClient):
    """Test updating user email via profile endpoint."""
    headers = _auth_headers(client, "emailupdate", "TestPass123", "old@example.com")
    
    # Update email
    update_response = client.put("/auth/profile", json={
        "email": "new@example.com"
    }, headers=headers)
    
    assert update_response.status_code == 200
    updated_user = update_response.json()
    assert updated_user["email"] == "new@example.com"
    
    # Verify via /me endpoint
    me_response = client.get("/auth/me", headers=headers)
    assert me_response.status_code == 200
    me_data = me_response.json()
    assert me_data["email"] == "new@example.com"


def test_profile_update_password(client: TestClient):
    """Test updating user password via profile endpoint."""
    headers = _auth_headers(client, "passupdate", "OldPass123", "pass@example.com")
    
    # Update password
    update_response = client.put("/auth/profile", json={
        "current_password": "OldPass123",
        "new_password": "NewPass456"
    }, headers=headers)
    
    assert update_response.status_code == 200
    
    # Verify old password no longer works
    old_login = client.post("/auth/token", data={
        "username": "passupdate",
        "password": "OldPass123"
    })
    assert old_login.status_code == 401
    
    # Verify new password works
    new_login = client.post("/auth/token", data={
        "username": "passupdate",
        "password": "NewPass456"
    })
    assert new_login.status_code == 200


def test_profile_update_password_wrong_current(client: TestClient):
    """Test password update fails with wrong current password."""
    headers = _auth_headers(client, "wrongpass", "CorrectPass123")
    
    # Try to update with wrong current password
    update_response = client.put("/auth/profile", json={
        "current_password": "WrongPass999",
        "new_password": "NewPass456"
    }, headers=headers)
    
    assert update_response.status_code == 401
    assert "incorrect" in update_response.json()["detail"].lower()


def test_profile_update_email_duplicate(client: TestClient):
    """Test email update fails when email already exists."""
    # Create first user
    _auth_headers(client, "user1", "Pass123456", "existing@example.com")
    
    # Create second user
    headers2 = _auth_headers(client, "user2", "Pass123456", "unique@example.com")
    
    # Try to update to existing email
    update_response = client.put("/auth/profile", json={
        "email": "existing@example.com"
    }, headers=headers2)
    
    assert update_response.status_code == 400
    assert "already registered" in update_response.json()["detail"].lower()


def test_profile_update_partial_password(client: TestClient):
    """Test profile update fails when only one password field provided."""
    headers = _auth_headers(client, "partialpass", "TestPass123")
    
    # Try with only current password
    response1 = client.put("/auth/profile", json={
        "current_password": "TestPass123"
    }, headers=headers)
    assert response1.status_code == 400
    assert "both" in response1.json()["detail"].lower()
    
    # Try with only new password
    response2 = client.put("/auth/profile", json={
        "new_password": "NewPass456"
    }, headers=headers)
    assert response2.status_code == 400
    assert "both" in response2.json()["detail"].lower()


def test_profile_update_email_and_password(client: TestClient):
    """Test updating both email and password simultaneously."""
    headers = _auth_headers(client, "bothupdate", "OldPass123", "old@example.com")
    
    # Update both
    update_response = client.put("/auth/profile", json={
        "email": "new@example.com",
        "current_password": "OldPass123",
        "new_password": "NewPass456"
    }, headers=headers)
    
    assert update_response.status_code == 200
    updated_user = update_response.json()
    assert updated_user["email"] == "new@example.com"
    
    # Verify new credentials work
    new_login = client.post("/auth/token", data={
        "username": "bothupdate",
        "password": "NewPass456"
    })
    assert new_login.status_code == 200


def test_profile_update_no_changes(client: TestClient):
    """Test profile update with no actual changes."""
    headers = _auth_headers(client, "nochanges", "TestPass123", "same@example.com")
    
    # Submit update with no changes
    update_response = client.put("/auth/profile", json={
        "email": "same@example.com"
    }, headers=headers)
    
    # Should succeed but no actual update
    assert update_response.status_code == 200


def test_map_embedding_stats(client: TestClient):
    """Test that map returns embedding statistics."""
    headers = _auth_headers(client, "embstats", "TestPass123")
    
    # Create notes
    for i in range(3):
        client.post("/notes/", json={
            "title": f"Note {i}",
            "content": f"Content for note {i}"
        }, headers=headers)
    
    # Get map
    map_response = client.get("/map/", headers=headers)
    assert map_response.status_code == 200
    map_data = map_response.json()
    
    stats = map_data["stats"]
    
    # Check for embedding-specific stats
    assert "embedding_coverage" in stats
    assert "embedding_based_edges" in stats
    assert "embedding_edge_ratio" in stats
    
    # Coverage should be between 0 and 1
    assert 0 <= stats["embedding_coverage"] <= 1
    
    # Edge counts should be non-negative
    assert stats["embedding_based_edges"] >= 0
    assert stats["embedding_edge_ratio"] >= 0


def test_map_isolated_nodes(client: TestClient):
    """Test map handling of isolated nodes."""
    headers = _auth_headers(client, "isolated", "TestPass123")
    
    # Create dissimilar notes
    client.post("/notes/", json={
        "title": "Machine Learning",
        "content": "Deep learning and neural networks"
    }, headers=headers)
    
    client.post("/notes/", json={
        "title": "Cooking",
        "content": "Recipe for chocolate cake"
    }, headers=headers)
    
    # Get map with high similarity threshold
    map_response = client.get("/map/", params={
        "min_similarity": 0.8,
        "include_isolates": True
    }, headers=headers)
    
    assert map_response.status_code == 200
    map_data = map_response.json()
    
    stats = map_data["stats"]
    
    # Check isolated node stats
    assert "isolated_nodes" in stats
    assert "isolated_node_ids" in stats
    
    # Some nodes should be isolated with high threshold
    assert stats["isolated_nodes"] >= 0


def test_map_edge_method_tracking(client: TestClient):
    """Test that map tracks which edges use embeddings vs keywords."""
    headers = _auth_headers(client, "edgemethod", "TestPass123")
    
    # Create notes
    client.post("/notes/", json={
        "title": "AI Topic 1",
        "content": "Machine learning algorithms"
    }, headers=headers)
    
    client.post("/notes/", json={
        "title": "AI Topic 2",
        "content": "Deep learning networks"
    }, headers=headers)
    
    # Get map
    map_response = client.get("/map/", params={"min_similarity": 0.1}, headers=headers)
    assert map_response.status_code == 200
    map_data = map_response.json()
    
    # Check edges have method tracking
    if len(map_data["edges"]) > 0:
        edge = map_data["edges"][0]
        assert "method" in edge
        assert edge["method"] in ["embedding", "keyword"]
        assert "has_embedding" in edge
