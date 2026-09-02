from fastapi.testclient import TestClient


def test_health_endpoint(client: TestClient):
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"message": "RecallAI API is running"}


def test_local_frontend_origin_receives_cors_headers(client: TestClient):
    response = client.options(
        "/topics/1",
        headers={
            "Origin": "http://127.0.0.1:5500",
            "Access-Control-Request-Method": "PUT",
        },
    )
    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://127.0.0.1:5500"
    assert "PUT" in response.headers["access-control-allow-methods"]
