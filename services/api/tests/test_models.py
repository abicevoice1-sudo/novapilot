"""Models catalog + token auth behavior."""

from fastapi.testclient import TestClient

from app import gateway_dep
from app.config import settings
from app.main import app

from .stub_gateway import stub_gateway


def test_models_lists_catalog():
    gateway_dep.override_gateway(stub_gateway())
    try:
        with TestClient(app) as client:
            r = client.get("/api/models")
            assert r.status_code == 200
            body = r.json()
            assert body["default"] == "test/echo"
            assert body["models"][0]["id"] == "ollama/gpt-oss:20b"
            assert all("provider" in m for m in body["models"])
    finally:
        gateway_dep.override_gateway(None)


def test_token_auth_enforced_when_set():
    old = settings.actlet_token
    settings.actlet_token = "s3cret"
    try:
        with TestClient(app) as client:
            assert client.get("/api/models").status_code == 401
            r = client.get("/api/models", headers={"Authorization": "Bearer s3cret"})
            assert r.status_code == 200
            assert client.get("/health").status_code == 200  # health stays public
    finally:
        settings.actlet_token = old
