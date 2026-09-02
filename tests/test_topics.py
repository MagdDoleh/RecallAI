from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from backend.models import Flashcard, QuizQuestion, Topic
from tests.conftest import auth_headers, login_user, register_user


def create_authenticated_user(client: TestClient, username: str, email: str) -> dict[str, str]:
    register_user(client, username, email)
    return auth_headers(login_user(client, username))


def test_topic_crud_and_relationship_persistence(client: TestClient, database: Session, study_material: dict):
    headers = create_authenticated_user(client, "alice", "alice@example.com")
    created = client.post("/topics", json=study_material, headers=headers)
    assert created.status_code == 201
    topic_id = created.json()["id"]
    topic = database.get(Topic, topic_id)
    assert len(topic.flashcards) == 3
    assert len(topic.quiz_questions) == 3

    listed = client.get("/topics", headers=headers)
    assert listed.status_code == 200
    assert [item["title"] for item in listed.json()] == [study_material["topic"]]

    opened = client.get(f"/topics/{topic_id}", headers=headers)
    assert opened.status_code == 200
    assert opened.json()["summary"] == study_material["summary"]

    old_flashcard_ids = {card.id for card in topic.flashcards}
    old_quiz_ids = {question.id for question in topic.quiz_questions}
    updated_material = {**study_material, "topic": "Updated Database Design", "summary": "Updated summary."}
    updated_material["flashcards"] = [{"question": f"New question {index}", "answer": f"New answer {index}"} for index in range(3)]
    updated_material["quiz_questions"] = [{"question": f"New quiz {index}", "answer": f"New quiz answer {index}", "difficulty": "medium"} for index in range(3)]
    updated = client.put(f"/topics/{topic_id}", json=updated_material, headers=headers)
    assert updated.status_code == 200
    assert updated.json()["topic"] == "Updated Database Design"
    database.expire_all()
    assert database.query(Flashcard).filter(Flashcard.id.in_(old_flashcard_ids)).count() == 0
    assert database.query(QuizQuestion).filter(QuizQuestion.id.in_(old_quiz_ids)).count() == 0
    assert database.query(Flashcard).filter_by(topic_id=topic_id).count() == 3
    assert database.query(QuizQuestion).filter_by(topic_id=topic_id).count() == 3

    deleted = client.delete(f"/topics/{topic_id}", headers=headers)
    assert deleted.status_code == 204
    assert database.get(Topic, topic_id) is None
    assert database.query(Flashcard).filter_by(topic_id=topic_id).count() == 0
    assert database.query(QuizQuestion).filter_by(topic_id=topic_id).count() == 0


def test_ownership_is_enforced_for_read_update_delete_and_list(client: TestClient, study_material: dict):
    alice_headers = create_authenticated_user(client, "alice", "alice@example.com")
    bob_headers = create_authenticated_user(client, "bob", "bob@example.com")
    topic_id = client.post("/topics", json=study_material, headers=alice_headers).json()["id"]

    assert client.get(f"/topics/{topic_id}", headers=alice_headers).status_code == 200
    assert len(client.get("/topics", headers=alice_headers).json()) == 1
    assert client.get("/topics", headers=bob_headers).json() == []
    assert client.get("/topics?search=Database", headers=bob_headers).json() == []
    assert client.get(f"/topics/{topic_id}", headers=bob_headers).status_code == 404
    assert client.put(f"/topics/{topic_id}", json=study_material, headers=bob_headers).status_code == 404
    assert client.delete(f"/topics/{topic_id}", headers=bob_headers).status_code == 404
    assert client.get(f"/topics/{topic_id}", headers=alice_headers).status_code == 200


def test_search_matching_case_whitespace_and_no_results(client: TestClient, study_material: dict):
    headers = create_authenticated_user(client, "alice", "alice@example.com")
    client.post("/topics", json=study_material, headers=headers)
    client.post("/topics", json={**study_material, "topic": "Binary Search Trees"}, headers=headers)
    assert [item["title"] for item in client.get("/topics?search=normal", headers=headers).json()] == ["Database Normalization"]
    assert [item["title"] for item in client.get("/topics?search=NORMAL", headers=headers).json()] == ["Database Normalization"]
    assert [item["title"] for item in client.get("/topics?search=%20%20binary%20%20", headers=headers).json()] == ["Binary Search Trees"]
    assert client.get("/topics?search=missing", headers=headers).json() == []


def test_search_wildcards_are_literal(client: TestClient, study_material: dict):
    headers = create_authenticated_user(client, "alice", "alice@example.com")
    client.post("/topics", json={**study_material, "topic": "Percent % Topic"}, headers=headers)
    client.post("/topics", json={**study_material, "topic": "Ordinary Topic"}, headers=headers)
    results = client.get("/topics?search=%25", headers=headers).json()
    assert [item["title"] for item in results] == ["Percent % Topic"]


def test_nonexistent_topic_operations_return_not_found(client: TestClient, study_material: dict):
    headers = create_authenticated_user(client, "alice", "alice@example.com")
    assert client.get("/topics/99999", headers=headers).status_code == 404
    assert client.put("/topics/99999", json=study_material, headers=headers).status_code == 404
    assert client.delete("/topics/99999", headers=headers).status_code == 404


def test_all_topic_operations_require_authentication(client: TestClient, study_material: dict):
    assert client.post("/topics", json=study_material).status_code == 401
    assert client.get("/topics").status_code == 401
    assert client.get("/topics/1").status_code == 401
    assert client.put("/topics/1", json=study_material).status_code == 401
    assert client.delete("/topics/1").status_code == 401
