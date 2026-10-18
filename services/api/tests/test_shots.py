"""Browser shots endpoint: serving, traversal protection, tool registration."""

from fastapi.testclient import TestClient

from app import agent as agent_mod
from app.main import app

# Minimal valid PNG (1x1).
PNG = (
    b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"
    b"\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDATx\x9cc\xf8\x0f\x00"
    b"\x00\x01\x01\x00\x05\x18\xd8N\x00\x00\x00\x00IEND\xaeB`\x82"
)


def test_serve_shot():
    d = agent_mod.shots_dir()
    (d / "shot-0001.png").write_bytes(PNG)
    with TestClient(app) as client:
        r = client.get("/api/shots/shot-0001.png")
        assert r.status_code == 200
        assert r.headers["content-type"] == "image/png"
        assert r.content == PNG


def test_shot_not_found():
    with TestClient(app) as client:
        assert client.get("/api/shots/shot-9999.png").status_code == 404


def test_traversal_blocked():
    with TestClient(app) as client:
        assert client.get("/api/shots/..%2Fmain.py").status_code in (404, 422)
        assert client.get("/api/shots/x.txt").status_code == 404


def test_browser_tools_registered():
    runner = agent_mod.build_runner(memory_service=None)
    names = [s["name"] for s in runner.registry.specs()]
    for tool in (
        "browser_open", "browser_snapshot", "browser_read", "browser_click",
        "browser_fill", "browser_select", "browser_press", "browser_back",
        "browser_screenshot",
    ):
        assert tool in names, tool
        t = runner.registry.get(tool)
        assert t.requires_approval is True
        assert t.risk == "high"
