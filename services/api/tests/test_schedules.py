"""Schedule endpoints: CRUD, parsing, run-now, firing, pre-approved tools."""

import asyncio
import json as _json
import time

import pytest
from actlet_agent import TaskRunner
from actlet_agent.tools import Tool, ToolRegistry
from fastapi.testclient import TestClient
from langgraph.checkpoint.memory import InMemorySaver
from pydantic import BaseModel
from sqlalchemy import select

from app import agent as agent_mod
from app.db import Schedule as ScheduleRow
from app.db import SessionLocal
from app.main import app
from app.task_store import SqlTaskStore

from .fakes import ScriptedGateway


class _EchoArgs(BaseModel):
    text: str = "hi"


async def _echo(args: _EchoArgs):
    from actlet_agent.tools import ToolResult

    return ToolResult(ok=True, output=f"echo:{args.text}")


class _DangerArgs(BaseModel):
    pass


async def _danger(args: _DangerArgs):
    from actlet_agent.tools import ToolResult

    return ToolResult(ok=True, output="danger done")


def _registry():
    reg = ToolRegistry()
    reg.register(Tool("echo_tool", "echoes", _EchoArgs, _echo))
    reg.register(Tool("danger_tool", "dangerous", _DangerArgs, _danger, risk="high", requires_approval=True))
    return reg


def _plan(*steps):
    return _json.dumps([{"description": d, "tool": t, "args": a} for d, t, a in steps])


class _Scripts:
    def __init__(self, scripts):
        self.scripts = scripts


@pytest.fixture()
def client():
    scripts = _Scripts([])

    def factory():
        return ScriptedGateway(scripts=list(scripts.scripts))

    runner = TaskRunner(
        gateway_factory=factory, registry=_registry(),
        checkpointer=InMemorySaver(), store=SqlTaskStore(),
    )
    agent_mod.override_runner(runner)

    async def _wipe():
        try:
            async with SessionLocal() as s:
                for row in (await s.execute(select(ScheduleRow))).scalars().all():
                    await s.delete(row)
                await s.commit()
        except Exception:  # noqa: BLE001, S110 — tables may not exist yet on first run
            pass

    asyncio.run(_wipe())  # hermetic: no schedule leaks between tests
    try:
        with TestClient(app) as c:
            yield c, scripts
    finally:
        agent_mod.override_runner(None)
        asyncio.run(_wipe())


def test_create_with_natural_language(client):
    c, _ = client
    r = c.post("/api/schedules", json={
        "name": "morning brief", "goal": "summarize news",
        "when": "every morning at 8", "preapproved_tools": ["echo_tool"],
    })
    assert r.status_code == 200
    body = r.json()
    assert body["cron"] == "0 8 * * *"
    assert body["when"] == "cron 0 8 * * *"
    assert body["preapproved_tools"] == ["echo_tool"]
    assert body["enabled"] is True
    assert body["next_run_at"] is not None


def test_create_with_cron_and_interval(client):
    c, _ = client
    r = c.post("/api/schedules", json={"name": "c", "goal": "g", "cron": "30 9 * * mon"})
    assert r.status_code == 200
    assert r.json()["cron"] == "30 9 * * mon"
    r = c.post("/api/schedules", json={"name": "i", "goal": "g", "interval_sec": 300})
    assert r.json()["interval_sec"] == 300
    assert r.json()["when"] == "every 5m"


def test_create_rejects_bad_schedule(client):
    c, _ = client
    r = c.post("/api/schedules", json={"name": "x", "goal": "g", "when": "whenever"})
    assert r.status_code == 422
    r = c.post("/api/schedules", json={"name": "x", "goal": "g"})
    assert r.status_code == 400
    r = c.post("/api/schedules", json={
        "name": "x", "goal": "g", "when": "daily at 9", "cron": "0 9 * * *"})
    assert r.status_code == 400


def test_crud_cycle(client):
    c, _ = client
    sid = c.post("/api/schedules", json={"name": "t", "goal": "g", "when": "hourly"}).json()["id"]
    assert c.get("/api/schedules").json()["schedules"]
    assert c.get(f"/api/schedules/{sid}").json()["name"] == "t"

    r = c.patch(f"/api/schedules/{sid}", json={"enabled": False, "name": "t2"})
    assert r.json()["enabled"] is False
    assert r.json()["name"] == "t2"
    assert r.json()["next_run_at"] is None  # disabled -> unscheduled

    r = c.patch(f"/api/schedules/{sid}", json={"when": "every 2 hours"})
    assert r.json()["interval_sec"] == 7200

    assert c.delete(f"/api/schedules/{sid}").json()["deleted"] == sid
    assert c.get(f"/api/schedules/{sid}").status_code == 404


def test_run_now_creates_task(client):
    c, scripts = client
    scripts.scripts = [_plan(("say hi", "echo_tool", {"text": "hello"})), _json.dumps({"approved": True}), "done"]
    sid = c.post("/api/schedules", json={"name": "t", "goal": "say hi", "when": "hourly"}).json()["id"]
    r = c.post(f"/api/schedules/{sid}/run-now")
    assert r.status_code == 200
    task_id = r.json()["task_id"]
    assert task_id

    # task ran to completion (echo_tool needs no approval)
    for _ in range(40):
        st = c.get(f"/api/tasks/{task_id}").json()["status"]
        if st in ("completed", "failed"):
            break
        time.sleep(0.25)
    assert st == "completed"

    sched = c.get(f"/api/schedules/{sid}").json()
    assert sched["run_count"] >= 1
    assert sched["last_task_id"] == task_id


def test_schedule_fires_on_trigger(client):
    c, scripts = client
    scripts.scripts = [_plan(("say hi", "echo_tool", {"text": "hello"})), _json.dumps({"approved": True}), "done"]
    sid = c.post("/api/schedules", json={
        "name": "fast", "goal": "say hi", "interval_sec": 2}).json()["id"]
    try:
        for _ in range(60):
            sched = c.get(f"/api/schedules/{sid}").json()
            if sched["run_count"] >= 1:
                break
            time.sleep(0.5)
        assert sched["run_count"] >= 1
        for _ in range(40):
            task = c.get(f"/api/tasks/{sched['last_task_id']}").json()
            if task["status"] in ("completed", "failed"):
                break
            time.sleep(0.25)
        assert task["status"] == "completed"
    finally:
        c.delete(f"/api/schedules/{sid}")


def test_preapproved_tools_skip_gates(client):
    c, scripts = client
    # danger_tool requires approval, but the schedule pre-approves it.
    scripts.scripts = [_plan(("do danger", "danger_tool", {})), _json.dumps({"approved": True}), "done"]
    sid = c.post("/api/schedules", json={
        "name": "p", "goal": "do danger", "when": "hourly",
        "preapproved_tools": ["danger_tool"],
    }).json()["id"]
    task_id = c.post(f"/api/schedules/{sid}/run-now").json()["task_id"]

    for _ in range(40):
        st = c.get(f"/api/tasks/{task_id}").json()["status"]
        if st in ("completed", "failed", "waiting_approval", "paused"):
            break
        time.sleep(0.25)
    # No approval gate should have fired — the tool was pre-approved.
    assert st == "completed", f"expected completed without approval, got {st}"
    c.delete(f"/api/schedules/{sid}")
