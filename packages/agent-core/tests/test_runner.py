"""TaskRunner: lifecycle, approval, cancel, budget pause, reconcile."""

import asyncio
import json

import pytest
from langgraph.checkpoint.memory import InMemorySaver
from pydantic import BaseModel

from actlet_agent.runner import TaskRunner
from actlet_agent.tools import Tool, ToolRegistry, ToolResult

from .fakes import MemoryTaskStore, ScriptedGateway


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
    return ToolResult(ok=True, output="slow done")


def _registry():
    reg = ToolRegistry()
    reg.register(Tool("echo_tool", "echoes", _EchoArgs, _echo))
    reg.register(
        Tool("danger_tool", "dangerous", _DangerArgs, _danger, risk="high", requires_approval=True)
    )
    reg.register(Tool("slow_tool", "slow", _EchoArgs, _slow))
    return reg


def _plan(*steps):
    return json.dumps([{"description": d, "tool": t, "args": a} for d, t, a in steps])


def _runner(scripts, store=None, **gw_kw):
    store = store or MemoryTaskStore()
    gw_scripts = list(scripts)
    return (
        TaskRunner(
            gateway_factory=lambda: ScriptedGateway(scripts=gw_scripts, **gw_kw),
            registry=_registry(),
            checkpointer=InMemorySaver(),
            store=store,
        ),
        store,
    )


async def _wait_for(store, task_id, statuses, timeout=10):
    for _ in range(int(timeout * 10)):
        t = await store.get(task_id)
        if t["status"] in statuses:
            return t
        await asyncio.sleep(0.1)
    raise TimeoutError(f"task {task_id} never reached {statuses}; last={t['status']}")


async def test_run_to_completion_emits_events():
    runner, store = _runner(
        [_plan(("one", "echo_tool", {}), ("two", "echo_tool", {})), "All good."]
    )
    tid = await runner.create_task("say things")
    t = await _wait_for(store, tid, ("completed",))
    assert t["status"] == "completed"
    types = [e["type"] for e in await store.events(tid)]
    assert "task_started" in types
    assert "plan_created" in types
    assert types.count("tool_called") == 2
    assert "task_completed" in types


async def test_approval_flow_through_runner():
    runner, store = _runner([_plan(("danger", "danger_tool", {})), "done"])
    tid = await runner.create_task("do danger")
    await _wait_for(store, tid, ("waiting_approval",))
    types = [e["type"] for e in await store.events(tid)]
    assert "approval_required" in types
    await runner.approve(tid, True)
    t = await _wait_for(store, tid, ("completed",))
    assert t["status"] == "completed"


async def test_approval_rejected_skips():
    runner, store = _runner([_plan(("danger", "danger_tool", {})), "done"])
    tid = await runner.create_task("do danger")
    await _wait_for(store, tid, ("waiting_approval",))
    await runner.approve(tid, False)
    await _wait_for(store, tid, ("completed",))
    state = await runner.get_state(tid)
    assert state["plan"][0]["status"] == "skipped"


async def test_cancel_mid_run():
    runner, store = _runner([_plan(("slow", "slow_tool", {})), "done"])
    tid = await runner.create_task("go slow")
    await asyncio.sleep(0.5)  # let the step start
    await runner.cancel(tid)
    t = await _wait_for(store, tid, ("cancelled",))
    assert t["status"] == "cancelled"


async def test_budget_breach_pauses_with_explanation():
    runner, store = _runner(
        [_plan(("one", "echo_tool", {})), "done"], max_cost_usd=0.0
    )
    tid = await runner.create_task("expensive")
    t = await _wait_for(store, tid, ("paused",))
    assert "Budget exceeded" in (t["error"] or "")
    types = [e["type"] for e in await store.events(tid)]
    assert "budget_exceeded" in types


async def test_pause_and_resume():
    runner, store = _runner(
        [_plan(("one", "echo_tool", {}), ("two", "echo_tool", {})), "done"]
    )
    tid = await runner.create_task("pausable")
    await asyncio.sleep(0.3)
    await runner.pause(tid)
    t = await _wait_for(store, tid, ("paused", "completed"))
    if t["status"] == "paused":
        await runner.resume(tid)
        t = await _wait_for(store, tid, ("completed",))
    assert t["status"] == "completed"


async def test_reconcile_marks_interrupted_paused():
    store = MemoryTaskStore()
    runner, _ = _runner([], store=store)
    tid = await store.create("orphan", None, "thread-x")
    await store.update(tid, status="running")
    await runner.reconcile()
    t = await store.get(tid)
    assert t["status"] == "paused"
    assert "restart" in (t["error"] or "")


async def test_approve_unknown_task_raises():
    runner, _store = _runner([])
    with pytest.raises(ValueError):
        await runner.approve("nope", True)
