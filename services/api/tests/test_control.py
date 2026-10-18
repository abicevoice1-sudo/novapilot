"""Global agent control: pause/resume/status, quiet-hours logic."""

from datetime import UTC, datetime

import pytest
from fastapi.testclient import TestClient

from app import control as control_mod
from app.main import app


@pytest.fixture()
def client():
    control_mod.set_paused(False)
    with TestClient(app) as c:
        yield c
    control_mod.set_paused(False)


def test_pause_resume_status(client):
    assert client.get("/api/agent/status").json() == {"paused": False, "quiet_hours": False}
    assert client.post("/api/agent/pause").json() == {"paused": True}
    assert client.get("/api/agent/status").json()["paused"] is True
    assert client.post("/api/agent/resume").json() == {"paused": False}
    assert client.get("/api/agent/status").json()["paused"] is False


def test_quiet_hours_logic(monkeypatch):
    monkeypatch.setattr(control_mod.settings, "quiet_hours_start", "22:00")
    monkeypatch.setattr(control_mod.settings, "quiet_hours_end", "07:00")

    def at(h, m):
        return datetime(2026, 10, 18, h, m, tzinfo=UTC)

    assert control_mod.in_quiet_hours(at(23, 0)) is True
    assert control_mod.in_quiet_hours(at(3, 0)) is True
    assert control_mod.in_quiet_hours(at(12, 0)) is False
    assert control_mod.in_quiet_hours(at(7, 0)) is False  # end is exclusive

    # Daytime window
    monkeypatch.setattr(control_mod.settings, "quiet_hours_start", "13:00")
    monkeypatch.setattr(control_mod.settings, "quiet_hours_end", "14:00")
    assert control_mod.in_quiet_hours(at(13, 30)) is True
    assert control_mod.in_quiet_hours(at(15, 0)) is False

    # Unset = never quiet
    monkeypatch.setattr(control_mod.settings, "quiet_hours_start", "")
    monkeypatch.setattr(control_mod.settings, "quiet_hours_end", "")
    assert control_mod.in_quiet_hours(at(3, 0)) is False


def test_quiet_hours_bad_format_ignored(monkeypatch):
    monkeypatch.setattr(control_mod.settings, "quiet_hours_start", "not-a-time")
    monkeypatch.setattr(control_mod.settings, "quiet_hours_end", "25:99")
    now = datetime(2026, 10, 18, 3, 0, tzinfo=UTC)
    assert control_mod.in_quiet_hours(now) is False
