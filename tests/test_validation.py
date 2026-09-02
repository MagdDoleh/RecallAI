import pytest
from fastapi.testclient import TestClient

from tests.conftest import auth_headers, login_user, register_user


@pytest.fixture
def headers(client: TestClient) -> dict[str, str]:
    register_user(client, "alice", "alice@example.com")
    return auth_headers(login_user(client, "alice"))


def test_malformed_and_missing_request_bodies_are_controlled(client: TestClient, headers: dict[str, str]):
    malformed = client.post("/topics", content="{not valid json", headers={**headers, "Content-Type": "application/json"})
    assert malformed.status_code == 422
    assert "traceback" not in malformed.text.lower()
    missing = client.post("/topics", json={"topic": "Only a title"}, headers=headers)
    assert missing.status_code == 422


def test_wrong_field_types_are_rejected(client: TestClient, headers: dict[str, str], study_material: dict):
    invalid = {**study_material, "flashcards": "not a list"}
    assert client.post("/topics", json=invalid, headers=headers).status_code == 422
    invalid = {**study_material, "quiz_questions": [{"question": "Q", "answer": "A", "difficulty": "impossible"}] * 3}
    assert client.post("/topics", json=invalid, headers=headers).status_code == 422


def test_saved_topic_rejects_empty_whitespace_and_oversized_titles(client: TestClient, headers: dict[str, str], study_material: dict):
    for title in ["", "   ", "x" * 201, "x" * 20_000]:
        response = client.post("/topics", json={**study_material, "topic": title}, headers=headers)
        assert response.status_code == 422


def test_saved_topic_title_length_boundary(client: TestClient, headers: dict[str, str], study_material: dict):
    assert client.post("/topics", json={**study_material, "topic": "x" * 200}, headers=headers).status_code == 201
    assert client.post("/topics", json={**study_material, "topic": "x" * 201}, headers=headers).status_code == 422


def test_update_rejects_invalid_text_without_changing_saved_data(client: TestClient, headers: dict[str, str], study_material: dict):
    topic_id = client.post("/topics", json=study_material, headers=headers).json()["id"]
    invalid_materials = [
        {**study_material, "topic": "   "},
        {**study_material, "summary": "   "},
        {**study_material, "summary": "x" * 5001},
        {**study_material, "key_concepts": [{"name": "   ", "explanation": "Valid"}] * 3},
        {**study_material, "flashcards": [{"question": "Valid", "answer": "   "}] * 3},
        {**study_material, "quiz_questions": [{"question": "   ", "answer": "Valid", "difficulty": "easy"}] * 3},
    ]
    for material in invalid_materials:
        assert client.put(f"/topics/{topic_id}", json=material, headers=headers).status_code == 422
    reopened = client.get(f"/topics/{topic_id}", headers=headers).json()
    assert reopened["topic"] == study_material["topic"]
    assert reopened["summary"] == study_material["summary"]


def test_generated_collection_size_limits_are_enforced(client: TestClient, headers: dict[str, str], study_material: dict):
    for field in ["key_concepts", "flashcards", "quiz_questions"]:
        too_few = {**study_material, field: study_material[field][:2]}
        too_many = {**study_material, field: study_material[field] * 3}
        assert client.post("/topics", json=too_few, headers=headers).status_code == 422
        assert client.post("/topics", json=too_many, headers=headers).status_code == 422


def test_search_query_maximum_is_enforced(client: TestClient, headers: dict[str, str]):
    assert client.get(f"/topics?search={'x' * 200}", headers=headers).status_code == 200
    assert client.get(f"/topics?search={'x' * 201}", headers=headers).status_code == 422


def test_request_does_not_echo_sensitive_authentication_data(client: TestClient):
    password = "SensitivePassword123!"
    register_user(client, "alice", "alice@example.com", password)
    response = client.post("/auth/login", json={"identifier": "alice", "password": "incorrect"})
    assert password not in response.text
    assert "password_hash" not in response.text
