"""Milestone 3 acceptance: config loads, health endpoint answers."""

from fastapi.testclient import TestClient

from app.main import app, settings

client = TestClient(app)


def test_health_ok():
    r = client.get("/health")
    assert r.status_code == 200
    body = r.json()
    assert body["ok"] is True
    assert body["service"] == "actlet-api"
    assert body["milestone"] == 6


def test_settings_defaults():
    assert settings.task_max_cost_usd == 0.50
    assert settings.actlet_token == ""
