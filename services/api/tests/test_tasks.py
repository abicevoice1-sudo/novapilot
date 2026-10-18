"""Task endpoints: lifecycle, SSE events, approval, cancel."""

import asyncio
import json as _json
import time

import pytest
from fastapi.testclient import TestClient
from langgraph.checkpoint.memory import InMemorySaver
from novapilot_agent.runner import TaskRunner
from novapilot_agent.tools import Tool, ToolRegistry, ToolResult
from pydantic import BaseModel

from app import agent as agent_mod
from app.main import app
from app.task_store import SqlTaskStore

from .fakes import ScriptedGateway


class _EchoArgs(BaseModel):
    text: str = "hi"


async def _echo(args: _EchoArgs) -> ToolResult:
    return ToolResult(ok=True, output=f"echo:{args.text}", verification="echoed")


class _DangerArgs(BaseModel):
    text: str = "x"


async def _danger(args: _DangerArgs) -> ToolResult:
    return ToolResult(ok=True, output="danger done", verification="did it")


async def _slow(args: _EchoArgs) -> ToolResult:
    await asyncio.sleep(30)
    return ToolResult(ok=True, output="slow")


def _registry():
    reg = ToolRegistry()
    reg.register(Tool("echo_tool", "echoes", _EchoArgs, _echo))
    reg.register(
        Tool("danger_tool", "dangerous", _DangerArgs, _danger, risk="high", requires_approval=True)
    )
    reg.register(Tool("slow_tool", "slow", _EchoArgs, _slow))
    return reg


def _plan(*steps):
    return _json.dumps([{"description": d, "tool": t, "args": a} for d, t, a in steps])


class _Scripts:
    """Mutable holder so the gateway factory serves fresh scripts per task."""

    def __init__(self, scripts):
        self.scripts = scripts


def _test_runner(scripts_holder):
    def factory():
        return ScriptedGateway(scripts=list(scripts_holder.scripts))

    return TaskRunner(
        gateway_factory=factory,
        registry=_registry(),
        checkpointer=InMemorySaver(),
        store=SqlTaskStore(),
    )


@pytest.fixture()
def scripts():
    return _Scripts([])


@pytest.fixture()
def client(scripts):
    runner = _test_runner(scripts)
    agent_mod.override_runner(runner)
    try:
        with TestClient(app) as c:
            yield c, scripts
    finally:
        agent_mod.override_runner(None)


def _wait_status(c, tid, statuses, timeout=15):
    for _ in range(int(timeout * 5)):
        r = c.get(f"/api/tasks/{tid}")
        assert r.status_code == 200
        if r.json()["status"] in statuses:
            return r.json()
        time.sleep(0.2)
    raise TimeoutError(f"task {tid} never reached {statuses}")


def test_create_and_run_to_completion(client):
    c, scripts = client
    scripts.scripts = [_plan(("one", "echo_tool", {}), ("two", "echo_tool", {})), "All good."]
    r = c.post("/api/tasks", json={"goal": "say things"})
    assert r.status_code == 200
    tid = r.json()["id"]
    task = _wait_status(c, tid, ("completed",))
    assert task["total_steps"] == 2
    assert task["current_step"] == 2
    assert all(s["status"] == "done" for s in task["steps"])
    assert task["summary"] == "All good."


def test_list_tasks(client):
    c, scripts = client
    scripts.scripts = [_plan(("one", "echo_tool", {})), "done"]
    c.post("/api/tasks", json={"goal": "listed goal"})
    tasks = c.get("/api/tasks").json()["tasks"]
    assert any(t["goal"] == "listed goal" for t in tasks)


def test_events_sse_replays_and_streams(client):
    c, scripts = client
    scripts.scripts = [_plan(("one", "echo_tool", {})), "done"]
    tid = c.post("/api/tasks", json={"goal": "stream me"}).json()["id"]
    _wait_status(c, tid, ("completed",))
    with c.stream("GET", f"/api/tasks/{tid}/events") as r:
        assert r.status_code == 200
        kinds = []
        for line in r.iter_lines():
            if line.startswith("data: "):
                kinds.append(_json.loads(line[6:])["type"])
                if kinds[-1] == "task_completed":
                    break
    assert "task_started" in kinds
    assert "plan_created" in kinds
    assert "tool_called" in kinds
    assert kinds[-1] == "task_completed"
    # sequence numbers are monotonic
    seqs = []
    with c.stream("GET", f"/api/tasks/{tid}/events") as r:
        for line in r.iter_lines():
            if line.startswith("data: "):
                seqs.append(_json.loads(line[6:])["seq"])
                if len(seqs) > 6:
                    break
    assert seqs == sorted(seqs)


def test_approval_flow(client):
    c, scripts = client
    scripts.scripts = [_plan(("danger", "danger_tool", {})), "done"]
    tid = c.post("/api/tasks", json={"goal": "do danger"}).json()["id"]
    _wait_status(c, tid, ("waiting_approval",))
    detail = c.get(f"/api/tasks/{tid}").json()
    assert detail["status"] == "waiting_approval"
    r = c.post(f"/api/tasks/{tid}/approve", json={"approved": True})
    assert r.status_code == 200
    task = _wait_status(c, tid, ("completed",))
    assert task["steps"][0]["status"] == "done"


def test_approve_rejected_skips_step(client):
    c, scripts = client
    scripts.scripts = [_plan(("danger", "danger_tool", {})), "done"]
    tid = c.post("/api/tasks", json={"goal": "do danger"}).json()["id"]
    _wait_status(c, tid, ("waiting_approval",))
    c.post(f"/api/tasks/{tid}/approve", json={"approved": False})
    task = _wait_status(c, tid, ("completed",))
    assert task["steps"][0]["status"] == "skipped"


def test_approve_when_not_waiting_409(client):
    c, scripts = client
    scripts.scripts = [_plan(("one", "echo_tool", {})), "done"]
    tid = c.post("/api/tasks", json={"goal": "x"}).json()["id"]
    _wait_status(c, tid, ("completed",))
    r = c.post(f"/api/tasks/{tid}/approve", json={"approved": True})
    assert r.status_code == 409


def test_cancel_mid_run(client):
    c, scripts = client
    scripts.scripts = [_plan(("slow", "slow_tool", {})), "done"]
    tid = c.post("/api/tasks", json={"goal": "go slow"}).json()["id"]
    time.sleep(0.5)
    r = c.post(f"/api/tasks/{tid}/cancel")
    assert r.status_code == 200
    task = _wait_status(c, tid, ("cancelled",))
    assert task["status"] == "cancelled"


def test_create_requires_goal(client):
    c, _ = client
    r = c.post("/api/tasks", json={"goal": "  "})
    assert r.status_code == 400


def test_unknown_task_404(client):
    c, _ = client
    assert c.get("/api/tasks/nope").status_code == 404
    assert c.get("/api/tasks/nope/events").status_code == 404
