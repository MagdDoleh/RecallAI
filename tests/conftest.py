import os
from collections.abc import Generator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker


os.environ["RECALLAI_JWT_SECRET"] = "test-only-jwt-secret-that-is-at-least-32-characters"
os.environ["GEMINI_API_KEY"] = ""

from backend import database as database_module  # noqa: E402


# Importing the application normally initializes recallai.db. Tests create their own
# schema below, so suppress only that import-time development initialization.
original_create_database_tables = database_module.create_database_tables
database_module.create_database_tables = lambda: None
from backend.main import app  # noqa: E402
database_module.create_database_tables = original_create_database_tables

from backend.database import Base, get_database_session  # noqa: E402


@pytest.fixture
def database(tmp_path: Path) -> Generator[Session, None, None]:
    database_path = tmp_path / "recallai-test.db"
    engine = create_engine(
        f"sqlite:///{database_path.as_posix()}",
        connect_args={"check_same_thread": False},
    )
    Base.metadata.create_all(bind=engine)
    TestSession = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    session = TestSession()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


@pytest.fixture
def client(database: Session) -> Generator[TestClient, None, None]:
    def override_database() -> Generator[Session, None, None]:
        yield database

    app.dependency_overrides[get_database_session] = override_database
    with TestClient(app, raise_server_exceptions=False) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def study_material() -> dict:
    return {
        "topic": "Database Normalization",
        "summary": "Normalization organizes relational data and reduces redundancy.",
        "key_concepts": [
            {"name": "First normal form", "explanation": "Each value is atomic."},
            {"name": "Second normal form", "explanation": "Remove partial dependencies."},
            {"name": "Third normal form", "explanation": "Remove transitive dependencies."},
        ],
        "flashcards": [
            {"question": "What is 1NF?", "answer": "Values are atomic."},
            {"question": "What is 2NF?", "answer": "No partial dependencies."},
            {"question": "What is 3NF?", "answer": "No transitive dependencies."},
        ],
        "quiz_questions": [
            {"question": "Which form requires atomic values?", "answer": "1NF", "difficulty": "easy"},
            {"question": "What does 2NF remove?", "answer": "Partial dependencies", "difficulty": "medium"},
            {"question": "What does 3NF remove?", "answer": "Transitive dependencies", "difficulty": "hard"},
        ],
    }


def register_user(client: TestClient, username: str, email: str, password: str = "SecurePass123!") -> dict:
    response = client.post(
        "/auth/register",
        json={"username": username, "email": email, "password": password},
    )
    assert response.status_code == 201
    return response.json()


def login_user(client: TestClient, identifier: str, password: str = "SecurePass123!") -> str:
    response = client.post(
        "/auth/login",
        json={"identifier": identifier, "password": password},
    )
    assert response.status_code == 200
    return response.json()["access_token"]


def auth_headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}
