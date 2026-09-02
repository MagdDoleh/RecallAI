from fastapi.testclient import TestClient

from backend.schemas import StudyMaterialResponse
from backend.services import gemini
from tests.conftest import auth_headers, login_user, register_user


def authenticated_headers(client: TestClient) -> dict[str, str]:
    register_user(client, "alice", "alice@example.com")
    return auth_headers(login_user(client, "alice"))


def test_generation_returns_mocked_structured_material(client: TestClient, monkeypatch, study_material: dict):
    headers = authenticated_headers(client)
    calls = []

    def fake_generation(topic: str) -> StudyMaterialResponse:
        calls.append(topic)
        return StudyMaterialResponse(**{**study_material, "topic": topic})

    monkeypatch.setattr(gemini, "generate_study_material", fake_generation)
    response = client.post("/generate", json={"topic": "  Database Normalization  "}, headers=headers)
    assert response.status_code == 200
    assert response.json()["topic"] == "Database Normalization"
    assert calls == ["Database Normalization"]


def test_invalid_generation_input_never_calls_gemini(client: TestClient, monkeypatch):
    headers = authenticated_headers(client)
    calls = []
    monkeypatch.setattr(gemini, "generate_study_material", lambda topic: calls.append(topic))
    invalid_topics = ["", "   ", "--!!", "x" * 201, "x" * 20_000]
    for topic in invalid_topics:
        assert client.post("/generate", json={"topic": topic}, headers=headers).status_code == 422
    assert calls == []


def test_generation_topic_length_boundaries(client: TestClient, monkeypatch, study_material: dict):
    headers = authenticated_headers(client)
    calls = []

    def fake_generation(topic: str) -> StudyMaterialResponse:
        calls.append(topic)
        return StudyMaterialResponse(**{**study_material, "topic": topic})

    monkeypatch.setattr(gemini, "generate_study_material", fake_generation)
    for length in [199, 200]:
        response = client.post("/generate", json={"topic": "x" * length}, headers=headers)
        assert response.status_code == 200
    assert client.post("/generate", json={"topic": "x" * 201}, headers=headers).status_code == 422
    assert [len(topic) for topic in calls] == [199, 200]


def test_generation_requires_authentication_before_gemini(client: TestClient, monkeypatch):
    calls = []
    monkeypatch.setattr(gemini, "generate_study_material", lambda topic: calls.append(topic))
    assert client.post("/generate", json={"topic": "Valid topic"}).status_code == 401
    assert calls == []


def test_gemini_configuration_failure_is_controlled(client: TestClient, monkeypatch):
    headers = authenticated_headers(client)
    monkeypatch.setattr(gemini, "generate_study_material", lambda topic: (_ for _ in ()).throw(gemini.GeminiNotConfiguredError()))
    response = client.post("/generate", json={"topic": "Valid topic"}, headers=headers)
    assert response.status_code == 503
    assert "GEMINI_API_KEY" in response.json()["detail"]
    assert "traceback" not in response.text.lower()


def test_gemini_api_and_timeout_failures_are_controlled(client: TestClient, monkeypatch):
    headers = authenticated_headers(client)
    monkeypatch.setattr(gemini, "generate_study_material", lambda topic: (_ for _ in ()).throw(gemini.GeminiGenerationError()))
    response = client.post("/generate", json={"topic": "Valid topic"}, headers=headers)
    assert response.status_code == 502
    assert response.json()["detail"] == "Gemini could not generate study material. Check the API key and try again."
    assert "traceback" not in response.text.lower()


def test_malformed_gemini_response_is_controlled(client: TestClient, monkeypatch):
    headers = authenticated_headers(client)
    monkeypatch.setattr(gemini, "generate_study_material", lambda topic: (_ for _ in ()).throw(gemini.GeminiResponseError()))
    response = client.post("/generate", json={"topic": "Valid topic"}, headers=headers)
    assert response.status_code == 502
    assert "unexpected format" in response.json()["detail"]
    assert "traceback" not in response.text.lower()
