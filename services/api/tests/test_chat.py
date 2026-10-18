"""Chat endpoint: SSE streaming, persistence, error events."""

from fastapi.testclient import TestClient

from app import gateway_dep
from app.main import app

from .stub_gateway import StubBackend, stub_gateway


def _client():
    return TestClient(app)


def test_chat_streams_and_persists():
    import json as _json

    gateway_dep.override_gateway(stub_gateway())
    try:
        with _client() as client:
            r = client.post("/api/chat", json={"messages": [{"role": "user", "content": "hi"}]})
            assert r.status_code == 200
            assert "text/event-stream" in r.headers["content-type"]
            events = [
                _json.loads(l.removeprefix("data: "))
                for l in r.text.splitlines()
                if l.startswith("data: ")
            ]
            kinds = [e["type"] for e in events]
            assert "delta" in kinds and kinds[-1] == "done"
            streamed = "".join(e.get("text", "") for e in events)
            assert streamed.strip() == "Hello from Nova."

            convs = client.get("/api/conversations").json()["conversations"]
            assert len(convs) >= 1
            msgs = client.get(f"/api/conversations/{convs[0]['id']}/messages").json()["messages"]
            roles = [m["role"] for m in msgs]
            assert "user" in roles and "assistant" in roles
            assert any("Hello from Nova." in m["content"] for m in msgs if m["role"] == "assistant")
    finally:
        gateway_dep.override_gateway(None)


def test_chat_continues_conversation():
    import json as _json

    gateway_dep.override_gateway(stub_gateway())
    try:
        with _client() as client:
            r1 = client.post("/api/chat", json={"messages": [{"role": "user", "content": "one"}]})
            done = _json.loads(
                next(l for l in r1.text.splitlines() if '"done"' in l).removeprefix("data: ")
            )
            r2 = client.post(
                "/api/chat",
                json={
                    "messages": [{"role": "user", "content": "two"}],
                    "conversation_id": done["conversation_id"],
                },
            )
            assert '"type": "done"' in r2.text
            msgs = client.get(f"/api/conversations/{done['conversation_id']}/messages").json()[
                "messages"
            ]
            assert sum(1 for m in msgs if m["role"] == "user") == 2
    finally:
        gateway_dep.override_gateway(None)


def test_chat_gateway_failure_emits_error_event():
    gateway_dep.override_gateway(stub_gateway(backend=StubBackend(fail=True)))
    try:
        with _client() as client:
            r = client.post("/api/chat", json={"messages": [{"role": "user", "content": "hi"}]})
            assert r.status_code == 200
            assert '"type": "error"' in r.text
            assert "no model reachable" in r.text
    finally:
        gateway_dep.override_gateway(None)


def test_chat_rejects_bad_role():
    with _client() as client:
        r = client.post("/api/chat", json={"messages": [{"role": "hacker", "content": "hi"}]})
        assert r.status_code == 422
