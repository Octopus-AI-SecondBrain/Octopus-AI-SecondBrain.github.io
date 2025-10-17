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


def _auth_headers(client: TestClient, username: str, password: str) -> dict[str, str]:
    """Create a user and return auth headers."""
    signup_response = client.post(
        "/auth/signup",
        json={"username": username, "password": password},
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
    # Create a test client with a fresh database that has no tables
    temp_db_path = TEST_ROOT / "empty_health_test.db"
    if temp_db_path.exists():
        temp_db_path.unlink()
    
    # Temporarily override the database URL for this test
    original_db_url = os.environ.get("SECONDBRAIN_DB_URL")
    os.environ["SECONDBRAIN_DB_URL"] = f"sqlite:///{temp_db_path}"
    
    try:
        with TestClient(app, base_url="http://localhost") as test_client:
            health_response = test_client.get("/health")
            
            # Should still return 200 but with degraded status
            assert health_response.status_code == 200
            response_data = health_response.json()
            assert response_data["status"] == "degraded"
            assert response_data["database"] == "schema_missing"
            assert "alembic upgrade head" in response_data["message"]
            
    finally:
        # Restore original environment
        if original_db_url:
            os.environ["SECONDBRAIN_DB_URL"] = original_db_url
        else:
            os.environ.pop("SECONDBRAIN_DB_URL", None)
            
        # Clean up test database
        if temp_db_path.exists():
            temp_db_path.unlink()
