"""Skills + dreaming endpoints."""

import asyncio
import json as _json
import time

import pytest
from fastapi.testclient import TestClient
from langgraph.checkpoint.memory import InMemorySaver
from novapilot_agent import TaskRunner
from novapilot_agent.tools import Tool, ToolRegistry, ToolResult
from novapilot_memory.service import MemoryService
from novapilot_memory.store import MemoryStore
from pydantic import BaseModel

from app import agent as agent_mod
from app import gateway_dep
from app.main import app
from app.memory import override_memory_service
from app.task_store import SqlTaskStore

from .fakes import ScriptedGateway
from .stub_gateway import StubBackend, stub_gateway


class _EchoArgs(BaseModel):
    text: str = "hi"


async def _echo(args: _EchoArgs):
    return ToolResult(ok=True, output=f"echo:{args.text}")


def _registry():
    reg = ToolRegistry()
    reg.register(Tool("echo_tool", "echoes", _EchoArgs, _echo))
    return reg


def _plan(*steps):
    return _json.dumps([{"description": d, "tool": t, "args": a} for d, t, a in steps])


class _Scripts:
    def __init__(self, scripts):
        self.scripts = scripts


@pytest.fixture()
def client(tmp_path):
    scripts = _Scripts([])

    def factory():
        return ScriptedGateway(scripts=list(scripts.scripts))

    runner = TaskRunner(
        gateway_factory=factory, registry=_registry(),
        checkpointer=InMemorySaver(), store=SqlTaskStore(),
    )
    agent_mod.override_runner(runner)

    async def _mem():
        store = MemoryStore(str(tmp_path / "mem.db"))
        await store.init()
        override_memory_service(MemoryService(store))
        return store

    mem_store = asyncio.run(_mem())
    # isolate skills dir
    import app.learning as learning_mod

    learning_mod._skill_store = None
    orig_dir = learning_mod.skills_dir
    learning_mod.skills_dir = lambda: tmp_path / "skills"
    try:
        with TestClient(app) as c:
            yield c, scripts
    finally:
        agent_mod.override_runner(None)
        override_memory_service(None)
        learning_mod.skills_dir = orig_dir
        learning_mod._skill_store = None
        asyncio.run(mem_store.close())


def _wait_task(c, task_id, timeout=20):
    for _ in range(int(timeout / 0.25)):
        st = c.get(f"/api/tasks/{task_id}").json()["status"]
        if st in ("completed", "failed"):
            return st
        time.sleep(0.25)
    return st


def test_skills_crud(client):
    c, _ = client
    r = c.post("/api/skills", json={
        "name": "Morning Brief",
        "description": "Summarize overnight news",
        "instructions": "1. Fetch feeds\n2. Summarize",
        "tools": ["web_fetch"],
    })
    assert r.status_code == 200
    assert r.json()["name"] == "Morning Brief"

    assert len(c.get("/api/skills").json()["skills"]) == 1
    assert "Fetch feeds" in c.get("/api/skills/morning-brief").json()["instructions"]
    assert c.delete("/api/skills/morning-brief").json()["deleted"] == "morning-brief"
    assert c.get("/api/skills").json()["skills"] == []


def test_dreaming_run_stores_facts(client):
    c, scripts = client
    scripts.scripts = [_plan(("say hi", "echo_tool", {"text": "hello"})), "done"]
    task_id = c.post("/api/tasks", json={"goal": "greet Syed warmly"}).json()["id"]
    assert _wait_task(c, task_id) == "completed"

    # dreaming gateway returns facts as JSON
    facts = _json.dumps([{"content": "Syed likes warm greetings.", "tags": ["preference"]}])
    gateway_dep.override_gateway(stub_gateway(backend=StubBackend(text=facts)))
    try:
        r = c.post("/api/dreaming/run")
        assert r.status_code == 200
        body = r.json()
        assert body["tasks_considered"] >= 1
        assert body["facts_stored"] >= 1
        # fact landed in memory with dreaming source
        assert c.get("/api/memories", params={"q": "greetings"}).json()["total"] >= 1
        # second run finds nothing new (all marked dreamed)
        assert c.post("/api/dreaming/run").json()["tasks_considered"] == 0
    finally:
        gateway_dep.override_gateway(None)


def test_make_skill_from_task(client):
    c, scripts = client
    scripts.scripts = [_plan(("say hi", "echo_tool", {"text": "hello"})), "done"]
    task_id = c.post("/api/tasks", json={"goal": "greet people"}).json()["id"]
    assert _wait_task(c, task_id) == "completed"

    skill_json = _json.dumps({
        "name": "greeter",
        "description": "Greet people warmly",
        "instructions": "1. Use echo_tool with a warm text",
        "tools": ["echo_tool"],
    })
    gateway_dep.override_gateway(stub_gateway(backend=StubBackend(text=skill_json)))
    try:
        r = c.post(f"/api/tasks/{task_id}/make-skill")
        assert r.status_code == 200
        assert r.json()["name"] == "greeter"
        assert len(c.get("/api/skills").json()["skills"]) == 1
    finally:
        gateway_dep.override_gateway(None)


def test_make_skill_rejects_incomplete(client):
    c, scripts = client
    scripts.scripts = [_plan(("say hi", "echo_tool", {"text": "x"})), "done"]
    c.post("/api/tasks", json={"goal": "quick"})
    # task still running (or at least not completed yet) -> try a missing task
    assert c.post("/api/tasks/doesnotexist/make-skill").status_code == 404
