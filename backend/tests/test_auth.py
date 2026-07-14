"""Auth API tests"""
import os
import pytest

# Set test database before importing app
os.environ["DATABASE_URL"] = "sqlite:///./data/test.db"

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool


SQLALCHEMY_DATABASE_URL = "sqlite:///./data/test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

# Import all models to register them with Base
from app.models import user  # noqa: F401
from app.models import document  # noqa: F401
from app.models import category  # noqa: F401
from app.models import chat  # noqa: F401
from app.models import permission  # noqa: F401
from app.models import config  # noqa: F401

from app.db.base import Base
from app.main import app
from app.deps import DBSession

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


class TestAuthAPI:
    """Test authentication API endpoints"""

    def test_register(self, client):
        """Test user registration."""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "username": "testuser",
                "email": "test@example.com",
                "password": "testpass123"
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert data["username"] == "testuser"
        assert data["email"] == "test@example.com"
        assert "id" in data

    def test_register_duplicate_username(self, client):
        """Test duplicate username registration fails."""
        client.post(
            "/api/v1/auth/register",
            json={
                "username": "duplicate",
                "email": "first@example.com",
                "password": "pass123"
            }
        )
        response = client.post(
            "/api/v1/auth/register",
            json={
                "username": "duplicate",
                "email": "second@example.com",
                "password": "pass123"
            }
        )
        assert response.status_code == 400

    def test_login_success(self, client):
        """Test successful login."""
        client.post(
            "/api/v1/auth/register",
            json={
                "username": "loginuser",
                "email": "logintest@example.com",
                "password": "password123"
            }
        )

        response = client.post(
            "/api/v1/auth/login",
            data={
                "username": "loginuser",
                "password": "password123"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_login_wrong_password(self, client):
        """Test login with wrong password fails."""
        client.post(
            "/api/v1/auth/register",
            json={
                "username": "user2",
                "email": "user2@example.com",
                "password": "correctpassword"
            }
        )

        response = client.post(
            "/api/v1/auth/login",
            data={
                "username": "user2",
                "password": "wrongpassword"
            }
        )
        assert response.status_code == 401

    def test_get_current_user(self, client):
        """Test get current user info."""
        client.post(
            "/api/v1/auth/register",
            json={
                "username": "currentuser",
                "email": "current@example.com",
                "password": "pass123"
            }
        )

        login_response = client.post(
            "/api/v1/auth/login",
            data={
                "username": "currentuser",
                "password": "pass123"
            }
        )
        token = login_response.json()["access_token"]

        response = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "currentuser"