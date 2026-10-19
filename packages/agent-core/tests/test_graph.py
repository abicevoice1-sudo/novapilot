"""Graph: plan → execute → verify, approval interrupts, resume."""

import json

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import Command
from pydantic import BaseModel

from actlet_agent.graph import build_graph
from actlet_agent.tools import Tool, ToolRegistry, ToolResult

from .fakes import ScriptedGateway


class _EchoArgs(BaseModel):
    text: str = "hi"


async def _echo(args: _EchoArgs) -> ToolResult:
    return ToolResult(ok=True, output=f"echo:{args.text}", verification="echoed")


class _DangerArgs(BaseModel):
    text: str = "x"


async def _danger(args: _DangerArgs) -> ToolResult:
    return ToolResult(ok=True, output="danger done", verification="did it")


def _registry():
    reg = ToolRegistry()
    reg.register(Tool("echo_tool", "echoes", _EchoArgs, _echo))
    reg.register(
        Tool("danger_tool", "dangerous", _DangerArgs, _danger, risk="high", requires_approval=True)
    )
    return reg


def _plan_json(steps):
    return json.dumps([{"description": d, "tool": t, "args": a} for d, t, a in steps])


def _config(gateway, collect_events=None, control=None, thread_id="t1"):
    async def _noop(t, p):
        return None

    async def _collect(t, p):
        collect_events.append(t)

    return {
        "configurable": {
            "thread_id": thread_id,
            "emit": _collect if collect_events is not None else _noop,
            "control": control or {},
            "gateway": gateway,
        }
    }


async def test_full_run_to_completion():
    gw = ScriptedGateway(
        scripts=[
            _plan_json([("say one", "echo_tool", {"text": "one"}), ("say two", "echo_tool", {"text": "two"})]),
            json.dumps({"approved": True}),
            "All done.",
        ]
    )
    events = []
    graph = build_graph(_registry(), checkpointer=InMemorySaver())
    result = await graph.ainvoke(
        {"goal": "say things"}, _config(gw, collect_events=events)
    )
    assert result["status"] == "completed"
    assert [s["status"] for s in result["plan"]] == ["done", "done"]
    assert result["summary"] == "All done."
    assert "plan_created" in events and "task_completed" in events


async def test_invalid_plan_fails_cleanly():
    gw = ScriptedGateway(scripts=["not json at all", "still not json"])
    graph = build_graph(_registry(), checkpointer=InMemorySaver())
    result = await graph.ainvoke({"goal": "x"}, _config(gw))
    assert result["status"] == "failed"
    assert "planning failed" in result["error"]


async def test_approval_interrupt_and_resume_approved():
    gw = ScriptedGateway(scripts=[_plan_json([("do danger", "danger_tool", {})]), json.dumps({"approved": True}), "done"])
    events = []
    control: dict = {}
    graph = build_graph(_registry(), checkpointer=InMemorySaver())
    cfg = _config(gw, collect_events=events, control=control)
    paused = await graph.ainvoke({"goal": "danger"}, cfg)
    assert "__interrupt__" in paused
    assert "approval_required" in events
    result = await graph.ainvoke(Command(resume=True), cfg)
    assert result["status"] == "completed"
    assert result["plan"][0]["status"] == "done"
    assert "approval_decided" in events
    # no duplicate approval request on resume
    assert events.count("approval_required") == 1


async def test_approval_rejected_skips_step():
    gw = ScriptedGateway(scripts=[_plan_json([("do danger", "danger_tool", {})]), json.dumps({"approved": True}), "done-ish"])
    control: dict = {}
    graph = build_graph(_registry(), checkpointer=InMemorySaver())
    cfg = _config(gw, control=control)
    paused = await graph.ainvoke({"goal": "danger"}, cfg)
    assert "__interrupt__" in paused
    result = await graph.ainvoke(Command(resume=False), cfg)
    assert result["status"] == "completed"
    assert result["plan"][0]["status"] == "skipped"


async def test_unknown_tool_in_plan_fails():
    gw = ScriptedGateway(scripts=[_plan_json([("bad", "nope_tool", {})]), _plan_json([("bad", "nope_tool", {})])])
    graph = build_graph(_registry(), checkpointer=InMemorySaver())
    result = await graph.ainvoke({"goal": "x"}, _config(gw))
    assert result["status"] == "failed"


async def test_planner_receives_relevant_skills():
    seen_prompts = []

    class _SpyGateway:
        async def chat(self, messages, model=None):
            seen_prompts.append(messages[-1]["content"])
            return _plan_json([("say hi", "echo_tool", {"text": "hi"})])

        def check_budget(self):
            pass

        def usage(self):
            return {}

    def provider(goal):
        assert "greet" in goal
        return [{"name": "greeter", "description": "Greet people warmly"}]

    graph = build_graph(_registry(), checkpointer=InMemorySaver(), skills_provider=provider)
    result = await graph.ainvoke({"goal": "greet Syed"}, _config(_SpyGateway()))
    assert result["status"] == "completed"
    assert "greeter" in seen_prompts[0]
    assert "Greet people warmly" in seen_prompts[0]


async def test_planner_survives_broken_skills_provider():
    def bad_provider(goal):
        raise RuntimeError("boom")

    gw = ScriptedGateway(scripts=[_plan_json([("say hi", "echo_tool", {"text": "hi"})]), json.dumps({"approved": True}), "done"])
    graph = build_graph(_registry(), checkpointer=InMemorySaver(), skills_provider=bad_provider)
    result = await graph.ainvoke({"goal": "x"}, _config(gw))
    assert result["status"] == "completed"
