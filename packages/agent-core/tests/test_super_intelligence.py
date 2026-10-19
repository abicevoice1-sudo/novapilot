"""Super-intelligence upgrades: critic node, smart memory, compression, image gen."""

import json
from unittest.mock import AsyncMock, patch

import httpx
import pytest
from langgraph.checkpoint.memory import InMemorySaver
from pydantic import BaseModel

from actlet_agent.graph import build_graph
from actlet_agent.tools import Tool, ToolRegistry, ToolResult, _generate_image, _ImageArgs

from .fakes import ScriptedGateway


class _EchoArgs(BaseModel):
    text: str = "hi"


async def _echo(args: _EchoArgs) -> ToolResult:
    return ToolResult(ok=True, output=f"echo:{args.text}", verification="echoed")


def _reg() -> ToolRegistry:
    reg = ToolRegistry()
    reg.register(Tool("echo", "Echo text", _EchoArgs, _echo))
    return reg


def _cfg(gateway):
    return {"configurable": {
        "gateway": gateway, "emit": AsyncMock(), "task_id": "t1", "thread_id": "t1",
    }}


PLAN = json.dumps([{"description": "say hi", "tool": "echo", "args": {"text": "hi"}}])


async def test_critic_approves_good_plan():
    gw = ScriptedGateway(scripts=[PLAN, json.dumps({"approved": True}), "done"])
    g = build_graph(_reg(), checkpointer=InMemorySaver())
    result = await g.ainvoke({"goal": "say hi"}, config=_cfg(gw))
    assert result["status"] == "completed"
    # plan + critic + summarize = 3 chat calls
    assert gw.chat_calls == 3


async def test_critic_rejects_then_replans():
    reject = json.dumps({
        "approved": False,
        "issues": ["missing verification"],
        "fix_hint": "add a verification step",
    })
    gw = ScriptedGateway(scripts=[
        PLAN,                      # initial plan
        reject,                    # critic rejects
        PLAN,                      # replan
        json.dumps({"approved": True}),  # critic approves
        "done",                    # summary
    ])
    events = []
    async def emit(t, p=None):
        events.append(t)
    cfg = {"configurable": {"gateway": gw, "emit": emit, "task_id": "t1", "thread_id": "t1"}}
    g = build_graph(_reg(), checkpointer=InMemorySaver())
    result = await g.ainvoke({"goal": "say hi"}, config=cfg)
    assert result["status"] == "completed"
    assert "plan_rejected" in events
    assert "plan_approved" in events


async def test_critic_failure_does_not_block():
    gw = ScriptedGateway(scripts=[PLAN, "not-json{{{", "done"])
    g = build_graph(_reg(), checkpointer=InMemorySaver())
    result = await g.ainvoke({"goal": "say hi"}, config=_cfg(gw))
    assert result["status"] == "completed"


# --- Image generation ---

async def test_generate_image_pollinations_ok():
    args = _ImageArgs(prompt="a sunset over mountains")
    mock_resp = AsyncMock()
    mock_resp.status_code = 200
    mock_resp.headers = {"content-type": "image/jpeg"}
    with patch("httpx.AsyncClient") as mock_client:
        mock_client.return_value.__aenter__.return_value.get.return_value = mock_resp
        result = await _generate_image(args)
    assert result.ok
    assert "pollinations.ai" in result.output
    assert result.artifacts["image_url"].startswith("https://image.pollinations.ai")


async def test_generate_image_both_fail_honest():
    args = _ImageArgs(prompt="a cat")
    with patch("httpx.AsyncClient") as mock_client:
        mock_client.return_value.__aenter__.return_value.get.side_effect = httpx.ConnectError("down")
        mock_client.return_value.__aenter__.return_value.post.side_effect = httpx.ConnectError("down")
        result = await _generate_image(args)
    assert not result.ok
    assert "unavailable" in result.output
    assert "HF_TOKEN" in result.output


def test_image_args_validation():
    from pydantic import ValidationError
    with pytest.raises(ValidationError):
        _ImageArgs(prompt="ab")  # too short
    with pytest.raises(ValidationError):
        _ImageArgs(prompt="x" * 501)  # too long
