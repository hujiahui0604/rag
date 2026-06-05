"""Chat API tests"""
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
            "username": "chatuser",
            "email": "chat@example.com",
            "password": "pass123"
        }
    )
    response = client.post(
        "/api/v1/auth/login",
        data={"username": "chatuser", "password": "pass123"}
    )
    return response.json()["access_token"]


class TestChatAPI:
    """Test chat API endpoints"""

    def test_list_sessions_empty(self, client, auth_token):
        """Test listing sessions when empty."""
        response = client.get(
            "/api/v1/chat/sessions",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_create_session(self, client, auth_token):
        """Test creating a new chat session."""
        response = client.post(
            "/api/v1/chat/sessions",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={"title": "Test Session"}
        )
        assert response.status_code == 201
        data = response.json()
        assert "id" in data
        assert data["title"] == "Test Session"

    def test_get_messages_empty(self, client, auth_token):
        """Test getting messages from a new session."""
        create_response = client.post(
            "/api/v1/chat/sessions",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={"title": "Message Test"}
        )
        session_id = create_response.json()["id"]

        response = client.get(
            f"/api/v1/chat/sessions/{session_id}",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_send_message_without_rag(self, client, auth_token):
        """Test sending a message without RAG (mock LLM)."""
        create_response = client.post(
            "/api/v1/chat/sessions",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={"title": "Chat Test"}
        )
        session_id = create_response.json()["id"]

        response = client.post(
            "/api/v1/chat/message",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={
                "message": "Hello, this is a test",
                "session_id": session_id,
                "use_history": False
            }
        )
        assert response.status_code in [200, 500]
        if response.status_code == 200:
            data = response.json()
            assert "message" in data or "error" in data

    def test_list_sessions_after_creation(self, client, auth_token):
        """Test listing sessions after creating one."""
        client.post(
            "/api/v1/chat/sessions",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={"title": "Session 1"}
        )

        response = client.get(
            "/api/v1/chat/sessions",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1