import pytest
from fastapi.testclient import TestClient
from fastapi import FastAPI
from sqlmodel import Session, create_engine, SQLModel
from sqlmodel.pool import StaticPool
from datetime import timedelta

from src.auth.controller import router as auth_router
from src.auth.service import (
    verify_password,
    get_password_hash,
    create_access_token,
    authenticate_user,
    create_user
)
from src.auth.models import UserDTO
from src.database import get_session


# Test database setup
@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session):
    def get_session_override():
        return session

    app = FastAPI()
    app.include_router(auth_router)
    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


class TestAuthService:
    def test_verify_password(self):
        password = "testpassword123"
        hashed = get_password_hash(password)
        assert verify_password(password, hashed) is True
        assert verify_password("wrongpassword", hashed) is False

    def test_get_password_hash(self):
        password = "testpassword123"
        hashed = get_password_hash(password)
        assert hashed != password
        assert verify_password(password, hashed) is True

    def test_create_access_token(self):
        data = {"sub": "testuser"}
        token = create_access_token(data)
        assert isinstance(token, str)
        assert len(token) > 0

    def test_create_access_token_with_expiry(self):
        data = {"sub": "testuser"}
        expires_delta = timedelta(minutes=30)
        token = create_access_token(data, expires_delta)
        assert isinstance(token, str)
        assert len(token) > 0

    def test_create_user(self, session: Session):
        user_dto = UserDTO(
            username="testuser",
            email="test@example.com",
            password="testpassword123",
            full_name="Test User"
        )
        user = create_user(user_dto, session)
        assert user.username == "testuser"
        assert user.email == "test@example.com"
        assert user.full_name == "Test User"
        assert user.disabled is False

    def test_authenticate_user_success(self, session: Session):
        user_dto = UserDTO(
            username="testuser",
            email="test@example.com",
            password="testpassword123"
        )
        create_user(user_dto, session)

        authenticated_user = authenticate_user("testuser", "testpassword123", session)
        assert authenticated_user is not False
        assert authenticated_user.username == "testuser"

    def test_authenticate_user_wrong_password(self, session: Session):
        user_dto = UserDTO(
            username="testuser",
            email="test@example.com",
            password="testpassword123"
        )
        create_user(user_dto, session)

        authenticated_user = authenticate_user("testuser", "wrongpassword", session)
        assert authenticated_user is False

    def test_authenticate_user_nonexistent(self, session: Session):
        authenticated_user = authenticate_user("nonexistent", "password", session)
        assert authenticated_user is False


class TestAuthController:
    def test_register_user(self, client: TestClient):
        user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpassword123",
            "full_name": "Test User"
        }
        response = client.post("/auth/register", json=user_data)
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "testuser"
        assert data["email"] == "test@example.com"
        assert data["full_name"] == "Test User"

    def test_register_duplicate_user(self, client: TestClient):
        user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpassword123"
        }
        # First registration
        client.post("/auth/register", json=user_data)
        # Second registration should fail
        response = client.post("/auth/register", json=user_data)
        assert response.status_code == 400

    def test_login_success(self, client: TestClient):
        # Register user first
        user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpassword123"
        }
        client.post("/auth/register", json=user_data)

        # Login
        login_data = {
            "username": "testuser",
            "password": "testpassword123"
        }
        response = client.post("/auth/token", json=login_data)
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_login_wrong_credentials(self, client: TestClient):
        login_data = {
            "username": "nonexistent",
            "password": "wrongpassword"
        }
        response = client.post("/auth/token", json=login_data)
        assert response.status_code == 401
