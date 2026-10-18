"""Memory endpoints: CRUD, search, redaction, export/import, extraction, chat recall."""

import asyncio
import json as _json

import pytest
from fastapi.testclient import TestClient
from novapilot_memory.service import MemoryService
from novapilot_memory.store import MemoryStore

from app import gateway_dep
from app.main import app
from app.memory import override_memory_service

from .stub_gateway import StubBackend, stub_gateway


@pytest.fixture()
def client(tmp_path):
    async def _setup():
        store = MemoryStore(str(tmp_path / "mem.db"))
        await store.init()
        override_memory_service(MemoryService(store))
        return store

    store = asyncio.run(_setup())
    try:
        with TestClient(app) as c:
            yield c
    finally:
        override_memory_service(None)
        asyncio.run(store.close())


def test_add_list_get(client):
    r = client.post("/api/memories", json={"content": "Syed prefers morning meetings.", "tags": ["preference"]})
    assert r.status_code == 200
    mid = r.json()["memory"]["id"]
    assert r.json()["merged"] is False

    body = client.get("/api/memories").json()
    assert body["total"] >= 1
    assert any(m["id"] == mid for m in body["memories"])

    one = client.get(f"/api/memories/{mid}").json()
    assert one["content"] == "Syed prefers morning meetings."
    assert one["tags"] == ["preference"]


def test_search_filters(client):
    client.post("/api/memories", json={"content": "Syed drinks chai in the morning."})
    client.post("/api/memories", json={"content": "The capital of France is Paris."})
    body = client.get("/api/memories", params={"q": "chai"}).json()
    assert body["total"] == 1
    assert "chai" in body["memories"][0]["content"]


def test_update_then_delete_honored(client):
    mid = client.post("/api/memories", json={"content": "old fact"}).json()["memory"]["id"]
    r = client.patch(f"/api/memories/{mid}", json={"content": "new fact"})
    assert r.status_code == 200
    assert r.json()["content"] == "new fact"

    assert client.delete(f"/api/memories/{mid}").status_code == 200
    assert client.get(f"/api/memories/{mid}").status_code == 404
    # honored everywhere: search no longer finds it
    assert client.get("/api/memories", params={"q": "fact"}).json()["total"] == 0


def test_redaction_on_write(client):
    r = client.post(
        "/api/memories", json={"content": "deploy key sk-abcdefghij1234567890xyz for prod"}
    )
    assert r.status_code == 200
    assert "[REDACTED]" in r.json()["memory"]["content"]
    assert "sk-abcdefghij" not in r.json()["memory"]["content"]


def test_secret_only_rejected(client):
    r = client.post("/api/memories", json={"content": "sk-abcdefghij1234567890xyz"})
    assert r.status_code == 400


def test_export_import_roundtrip(client):
    client.post("/api/memories", json={"content": "exportable fact", "tags": ["x"]})
    exported = client.get("/api/memories/export").json()["memories"]
    assert len(exported) >= 1

    for m in client.get("/api/memories").json()["memories"]:
        client.delete(f"/api/memories/{m['id']}")
    assert client.get("/api/memories").json()["total"] == 0

    r = client.post("/api/memories/import", json={"memories": exported})
    assert r.json()["added"] == len(exported)
    assert client.get("/api/memories").json()["total"] == len(exported)


def test_dedup_on_api(client):
    client.post("/api/memories", json={"content": "Syed prefers morning meetings."})
    r = client.post("/api/memories", json={"content": "Syed prefers morning meetings for standup."})
    assert r.json()["merged"] is True
    assert client.get("/api/memories").json()["total"] == 1


def test_extract_memories_from_conversation(client):
    # seed a conversation via chat (stubbed model)
    gateway_dep.override_gateway(stub_gateway())
    try:
        r = client.post("/api/chat", json={"messages": [{"role": "user", "content": "I love chai and morning meetings"}]})
        conv_id = _json.loads(next(l for l in r.text.splitlines() if '"done"' in l)[6:])["conversation_id"]

        # extraction stub returns facts as JSON
        extract_json = _json.dumps([{"content": "Syed loves chai.", "tags": ["preference"]}])
        gateway_dep.override_gateway(stub_gateway(backend=StubBackend(text=extract_json)))

        r = client.post(f"/api/conversations/{conv_id}/extract-memories")
        assert r.status_code == 200
        assert r.json()["count"] == 1
        assert client.get("/api/memories", params={"q": "chai"}).json()["total"] == 1
    finally:
        gateway_dep.override_gateway(None)


def test_chat_injects_recalled_memories(client):
    client.post("/api/memories", json={"content": "Syed's favorite editor is vim."})

    seen = {}

    class CaptureBackend(StubBackend):
        async def acompletion(self, model, messages, stream=False):
            seen["messages"] = messages
            return await super().acompletion(model, messages, stream=stream)

    gateway_dep.override_gateway(stub_gateway(backend=CaptureBackend()))
    try:
        client.post("/api/chat", json={"messages": [{"role": "user", "content": "which editor do I like?"}]})
    finally:
        gateway_dep.override_gateway(None)

    system_msgs = [m for m in seen["messages"] if m["role"] == "system"]
    assert len(system_msgs) == 1
    assert "vim" in system_msgs[0]["content"]
    assert "long-term memory" in system_msgs[0]["content"]


def test_chat_without_relevant_memory_has_no_injection(client):
    seen = {}

    class CaptureBackend(StubBackend):
        async def acompletion(self, model, messages, stream=False):
            seen["messages"] = messages
            return await super().acompletion(model, messages, stream=stream)

    gateway_dep.override_gateway(stub_gateway(backend=CaptureBackend()))
    try:
        client.post("/api/chat", json={"messages": [{"role": "user", "content": "hello there"}]})
    finally:
        gateway_dep.override_gateway(None)

    assert all(m["role"] != "system" for m in seen["messages"])
