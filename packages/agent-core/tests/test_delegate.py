"""Multi-agent delegation: specialists, restricted toolsets, no recursion."""

import asyncio
import json

import pytest
from langgraph.checkpoint.memory import InMemorySaver
from pydantic import BaseModel

from actlet_agent.delegate import SPECIALISTS, register_delegate_tool
from actlet_agent.runner import TaskRunner
from actlet_agent.tools import Tool, ToolRegistry, ToolResult

from .fakes import MemoryTaskStore, ScriptedGateway


class _NoArgs(BaseModel):
    pass


async def _echo(args: _NoArgs):
    return ToolResult(ok=True, output="echo!")


async def _write(args: _NoArgs):
    return ToolResult(ok=True, output="written")


def _registry():
    reg = ToolRegistry()
    reg.register(Tool("echo_tool", "echo", _NoArgs, _echo))
    reg.register(Tool("write_file", "write", _NoArgs, _write))
    reg.register(Tool("web_fetch", "fetch", _NoArgs, _echo))
    return reg


def _plan(*steps):
    return json.dumps([{"description": d, "tool": t, "args": a} for d, t, a in steps])


def _runner(scripts):
    store = MemoryTaskStore()
    gw_scripts = list(scripts)
    reg = _registry()
    runner = TaskRunner(
        gateway_factory=lambda: ScriptedGateway(scripts=gw_scripts),
        registry=reg,
        checkpointer=InMemorySaver(),
        store=store,
    )
    register_delegate_tool(reg, runner.run_delegate)
    return runner, store


async def _wait_for(store, task_id, statuses, timeout=15):
    for _ in range(int(timeout * 10)):
        t = await store.get(task_id)
        if t["status"] in statuses:
            return t
        await asyncio.sleep(0.1)
    raise TimeoutError(f"task {task_id} never reached {statuses}")


async def test_unknown_role_fails_cleanly():
    runner, _ = _runner([])
    reg = runner.registry
    result, _ = await reg.call("delegate", {"role": "astronaut", "goal": "go to mars"})
    assert result.ok is False
    assert "unknown role" in result.output


async def test_specialist_roles_defined():
    assert set(SPECIALISTS) == {"researcher", "coder", "browser_operator", "communicator"}
    for spec in SPECIALISTS.values():
        assert "delegate" not in spec["tools"]  # no recursive delegation


async def test_delegate_runs_specialist_and_returns_summary():
    # Parent delegates to researcher; researcher echoes and summarizes.
    runner, store = _runner(
        [
            _plan(("hand off", "delegate", {"role": "researcher", "goal": "find facts"})),
            "Parent done.",
            _plan(("look", "echo_tool", {})),
            "Researcher summary: facts found.",
        ]
    )
    tid = await runner.create_task("do research via specialist")
    t = await _wait_for(store, tid, ("completed",))
    assert t["status"] == "completed"
    # The delegate tool's output should contain the specialist's summary.
    state = await runner.get_state(tid)
    delegate_steps = [s for s in state["plan"] if s["tool"] == "delegate"]
    assert delegate_steps, "delegate step missing from plan"
    assert delegate_steps[0]["status"] == "done"


async def test_specialist_cannot_use_parent_only_tools():
    # The coder specialist's registry has no web_fetch; planning web_fetch fails.

    reg = _registry()
    coder_tools = SPECIALISTS["coder"]["tools"]
    sub = reg.subset(coder_tools)
    assert sub.get("web_fetch") is None
    assert sub.get("write_file") is not None
    assert sub.get("delegate") is None


async def test_delegate_outside_task_raises():
    runner, _ = _runner([])
    with pytest.raises(RuntimeError, match="outside a task"):
        await runner.run_delegate("researcher", "hello")
