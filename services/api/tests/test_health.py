"""Milestone 1 acceptance: config loads, health endpoint answers."""

from fastapi.testclient import TestClient

from app.main import app, settings

client = TestClient(app)


def test_health_ok():
    r = client.get("/health")
    assert r.status_code == 200
    body = r.json()
    assert body["ok"] is True
    assert body["service"] == "novapilot-api"
    assert body["milestone"] == 1


def test_settings_defaults():
    assert settings.model_default == "ollama/gpt-oss:20b"
    assert settings.task_max_cost_usd == 0.50
