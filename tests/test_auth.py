from datetime import UTC, datetime, timedelta

import jwt
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from backend.config import JWT_ALGORITHM, get_jwt_secret
from backend.models import User
from tests.conftest import auth_headers, login_user, register_user


def test_registration_returns_public_user_and_hashes_password(client: TestClient, database: Session):
    response = client.post("/auth/register", json={"username": "alice", "email": "ALICE@example.com", "password": "PlainPassword123!"})
    assert response.status_code == 201
    assert response.json()["email"] == "alice@example.com"
    assert "password" not in response.json()
    assert "password_hash" not in response.json()
    user = database.query(User).filter_by(username="alice").one()
    assert user.password_hash != "PlainPassword123!"
    assert user.password_hash.startswith("$argon2")


def test_login_and_current_user(client: TestClient):
    register_user(client, "alice", "alice@example.com")
    token = login_user(client, "ALICE")
    response = client.get("/auth/me", headers=auth_headers(token))
    assert response.status_code == 200
    assert response.json()["username"] == "alice"
    assert "password_hash" not in response.json()


def test_duplicate_username_is_case_insensitive(client: TestClient):
    register_user(client, "Alice", "alice@example.com")
    response = client.post("/auth/register", json={"username": "alice", "email": "other@example.com", "password": "SecurePass123!"})
    assert response.status_code == 409
    assert response.json()["detail"] == "That username is already registered."


def test_duplicate_email_is_case_insensitive(client: TestClient):
    register_user(client, "alice", "Alice@Example.com")
    response = client.post("/auth/register", json={"username": "other", "email": "alice@example.com", "password": "SecurePass123!"})
    assert response.status_code == 409
    assert response.json()["detail"] == "That email address is already registered."


def test_incorrect_password_and_unknown_account_share_controlled_error(client: TestClient):
    register_user(client, "alice", "alice@example.com")
    for identifier, password in [("alice", "wrong-password"), ("missing", "wrong-password")]:
        response = client.post("/auth/login", json={"identifier": identifier, "password": password})
        assert response.status_code == 401
        assert response.json()["detail"] == "Incorrect username, email, or password."


def test_protected_endpoint_requires_bearer_token(client: TestClient):
    response = client.get("/auth/me")
    assert response.status_code == 401
    assert "password" not in response.text.lower()


def test_malformed_and_invalid_signature_tokens_are_rejected(client: TestClient):
    register_user(client, "alice", "alice@example.com")
    invalid_signature = jwt.encode({"sub": "1", "exp": datetime.now(UTC) + timedelta(minutes=5)}, "different-test-secret-that-is-long-enough", algorithm=JWT_ALGORITHM)
    for token in ["not-a-jwt", invalid_signature]:
        response = client.get("/auth/me", headers=auth_headers(token))
        assert response.status_code == 401
        assert response.json()["detail"] == "Could not validate authentication credentials."


def test_expired_token_is_rejected(client: TestClient):
    register_user(client, "alice", "alice@example.com")
    token = jwt.encode({"sub": "1", "iat": datetime.now(UTC) - timedelta(hours=2), "exp": datetime.now(UTC) - timedelta(hours=1)}, get_jwt_secret(), algorithm=JWT_ALGORITHM)
    assert client.get("/auth/me", headers=auth_headers(token)).status_code == 401


def test_token_for_deleted_user_is_rejected(client: TestClient, database: Session):
    register_user(client, "alice", "alice@example.com")
    token = login_user(client, "alice")
    user = database.query(User).filter_by(username="alice").one()
    database.delete(user)
    database.commit()
    assert client.get("/auth/me", headers=auth_headers(token)).status_code == 401


def test_registration_validation_rejects_invalid_input(client: TestClient):
    invalid_payloads = [
        {"username": "ab", "email": "valid@example.com", "password": "SecurePass123!"},
        {"username": "bad name", "email": "valid@example.com", "password": "SecurePass123!"},
        {"username": "valid_name", "email": "not-an-email", "password": "SecurePass123!"},
        {"username": "valid_name", "email": "valid@example.com", "password": "short"},
    ]
    for payload in invalid_payloads:
        assert client.post("/auth/register", json=payload).status_code == 422
