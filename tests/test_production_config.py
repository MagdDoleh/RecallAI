from fastapi.testclient import TestClient

from backend import database
from backend.config import LOCAL_CORS_ORIGINS, get_cors_origins


def test_database_url_defaults_to_local_sqlite(monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    assert database.get_database_url() == database.LOCAL_DATABASE_URL


def test_render_postgres_url_selects_psycopg_driver(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "postgresql://user:password@database-host/database-name")
    assert database.get_database_url() == "postgresql+psycopg://user:password@database-host/database-name"


def test_legacy_postgres_scheme_selects_psycopg_driver(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "postgres://user:password@database-host/database-name")
    assert database.get_database_url() == "postgresql+psycopg://user:password@database-host/database-name"


def test_cors_defaults_to_local_development_origins(monkeypatch):
    monkeypatch.delenv("RECALLAI_CORS_ORIGINS", raising=False)
    assert get_cors_origins() == LOCAL_CORS_ORIGINS


def test_cors_uses_trimmed_configured_origins(monkeypatch):
    monkeypatch.setenv("RECALLAI_CORS_ORIGINS", "https://recallai.example.com/, https://study.example.com")
    assert get_cors_origins() == ["https://recallai.example.com", "https://study.example.com"]


def test_fastapi_serves_same_frontend_files_in_production(client: TestClient):
    for path in ["/", "/app"]:
        page = client.get(path)
        assert page.status_code == 200
        assert "text/html" in page.headers["content-type"]
        assert "RecallAI" in page.text
    assert client.get("/css/styles.css").status_code == 200
    javascript = client.get("/js/app.js")
    assert javascript.status_code == 200
    assert "window.location.origin" in javascript.text
