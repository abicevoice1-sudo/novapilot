"""Checkpoint revert endpoint."""

import json as _json
import time

import pytest
from actlet_agent import CheckpointManager, TaskRunner
from actlet_agent.tools import Tool, ToolRegistry, ToolResult
from fastapi.testclient import TestClient
from langgraph.checkpoint.memory import InMemorySaver
from pydantic import BaseModel

from app import agent as agent_mod
from app.main import app
from app.task_store import SqlTaskStore

from .fakes import ScriptedGateway


class _DangerArgs(BaseModel):
    path: str = "x.txt"
    content: str = "changed"


async def _danger(args: _DangerArgs):
    return ToolResult(ok=True, output="danger done")


def _registry():
    reg = ToolRegistry()
    reg.register(Tool("danger_tool", "dangerous", _DangerArgs, _danger,
                      risk="high", requires_approval=True))
    return reg


def _plan(*steps):
    return _json.dumps([{"description": d, "tool": t, "args": a} for d, t, a in steps])


@pytest.fixture()
def client(tmp_path):
    from app import agent as agent_pkg

    scripts = []

    def factory():
        return ScriptedGateway(scripts=list(scripts))

    mgr = CheckpointManager(tmp_path / "ws")
    (tmp_path / "ws" / "keep.txt").write_text("original")
    agent_pkg._checkpoint_manager = mgr  # hermetic workspace
    runner = TaskRunner(
        gateway_factory=factory, registry=_registry(),
        checkpointer=InMemorySaver(), store=SqlTaskStore(),
        checkpoint_manager=mgr,
    )
    agent_mod.override_runner(runner)
    try:
        with TestClient(app) as c:
            yield c, scripts
    finally:
        agent_mod.override_runner(None)
        agent_pkg._checkpoint_manager = None


def test_checkpoint_created_on_approved_step_and_revert(client):
    c, scripts = client
    scripts.extend([_plan(("do danger", "danger_tool", {"path": "x", "content": "y"})), "done"])
    task_id = c.post("/api/tasks", json={"goal": "do danger"}).json()["id"]

    # approve the gate
    for _ in range(40):
        st = c.get(f"/api/tasks/{task_id}").json()["status"]
        if st == "waiting_approval":
            break
        time.sleep(0.25)
    assert st == "waiting_approval"
    c.post(f"/api/tasks/{task_id}/approve", json={"approved": True})

    for _ in range(40):
        st = c.get(f"/api/tasks/{task_id}").json()["status"]
        if st == "completed":
            break
        time.sleep(0.25)
    assert st == "completed"

    # a checkpoint event was emitted
    events = c.get(f"/api/tasks/{task_id}/events", headers={"Accept": "text/event-stream"}).text
    assert "checkpoint_created" in events

    # revert works (workspace had keep.txt; restore is a no-op content-wise but must succeed)
    r = c.post(f"/api/tasks/{task_id}/revert")
    assert r.status_code == 200
    assert r.json()["reverted_to"]


def test_revert_no_checkpoints_404(client):
    c, scripts = client
    scripts.extend([_plan(("noop", "danger_tool", {})), "done"])
    # create a task but don't run any risky step — use a fresh id
    r = c.post("/api/tasks/doesnotexist/revert")
    assert r.status_code == 404
