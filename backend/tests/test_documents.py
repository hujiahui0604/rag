"""Document API tests"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.main import app
from app.deps import DBSession


SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[DBSession] = override_get_db


@pytest.fixture(scope="module")
def client():
    Base.metadata.create_all(bind=engine)
    yield TestClient(app)
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def auth_token(client):
    """Get authentication token."""
    client.post(
        "/api/v1/auth/register",
        json={
            "username": "docuser",
            "email": "doc@example.com",
            "password": "pass123"
        }
    )
    response = client.post(
        "/api/v1/auth/login",
        data={"username": "docuser", "password": "pass123"}
    )
    return response.json()["access_token"]


class TestDocumentAPI:
    """Test document API endpoints"""

    def test_list_documents_empty(self, client, auth_token):
        """Test listing documents when empty."""
        response = client.get(
            "/api/v1/documents",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["items"] == []
        assert data["total"] == 0

    def test_create_document(self, client, auth_token):
        """Test document upload."""
        import io
        file_content = b"Test document content"

        response = client.post(
            "/api/v1/documents",
            headers={"Authorization": f"Bearer {auth_token}"},
            data={
                "file": ("test.txt", io.BytesIO(file_content), "text/plain"),
                "title": "Test Document",
                "description": "A test document"
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Test Document"
        assert data["file_type"] == "txt"

    def test_get_document(self, client, auth_token):
        """Test getting document detail."""
        import io
        file_content = b"Test content for get"

        create_response = client.post(
            "/api/v1/documents",
            headers={"Authorization": f"Bearer {auth_token}"},
            data={
                "file": ("gettest.txt", io.BytesIO(file_content), "text/plain"),
                "title": "Get Test"
            }
        )
        doc_id = create_response.json()["id"]

        response = client.get(
            f"/api/v1/documents/{doc_id}",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Get Test"

    def test_update_document(self, client, auth_token):
        """Test updating document."""
        import io
        file_content = b"Content for update"

        create_response = client.post(
            "/api/v1/documents",
            headers={"Authorization": f"Bearer {auth_token}"},
            data={
                "file": ("updatetest.txt", io.BytesIO(file_content), "text/plain"),
                "title": "Original Title"
            }
        )
        doc_id = create_response.json()["id"]

        response = client.put(
            f"/api/v1/documents/{doc_id}",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={"title": "Updated Title", "description": "New description"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Updated Title"
        assert data["description"] == "New description"

    def test_delete_document(self, client, auth_token):
        """Test deleting document."""
        import io
        file_content = b"Content for delete"

        create_response = client.post(
            "/api/v1/documents",
            headers={"Authorization": f"Bearer {auth_token}"},
            data={
                "file": ("deletetest.txt", io.BytesIO(file_content), "text/plain"),
                "title": "Delete Me"
            }
        )
        doc_id = create_response.json()["id"]

        response = client.delete(
            f"/api/v1/documents/{doc_id}",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 204

    def test_list_documents_with_pagination(self, client, auth_token):
        """Test document list pagination."""
        response = client.get(
            "/api/v1/documents?page=1&page_size=10",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert "page" in data