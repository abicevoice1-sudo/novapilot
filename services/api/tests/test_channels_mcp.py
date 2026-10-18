"""Channels + MCP + skill import/export."""

import sys

import pytest
from fastapi.testclient import TestClient
from novapilot_agent.tools import ToolRegistry

from app.config import settings
from app.main import app

from .fakes import ScriptedGateway


@pytest.fixture()
def client():
    # No runner override needed; channels router doesn't touch the runner.
    # Lifespan builds a real runner — gateway is stubbed via MODEL_DEFAULT.
    with TestClient(app) as c:
        yield c


def test_channels_empty_when_unconfigured(client):
    assert client.get("/api/channels").json() == {"channels": {}}


class _FakeChannel:
    name = "fake"

    def __init__(self):
        self.sent = []
        self._task = True

    async def start(self, on_message):
        self._on_message = on_message

    async def stop(self):
        pass

    async def send(self, msg):
        self.sent.append(msg)


async def test_inbound_message_creates_task_and_replies():
    import asyncio as _asyncio

    from langgraph.checkpoint.memory import InMemorySaver
    from novapilot_agent import TaskRunner
    from novapilot_agent.tools import ToolRegistry
    from novapilot_channels import InboundMessage

    from app import agent as agent_mod
    from app import channels as channels_mod
    from app.db import init_db
    from app.task_store import SqlTaskStore

    runner = TaskRunner(
        gateway_factory=lambda: ScriptedGateway(scripts=[
            '[{"description": "d", "tool": "nope", "args": {}}]',
            '[{"description": "d", "tool": "nope", "args": {}}]',
        ]),
        registry=ToolRegistry(),
        checkpointer=InMemorySaver(),
        store=SqlTaskStore(),
    )
    await init_db()
    agent_mod.override_runner(runner)
    try:
        mgr = channels_mod.ChannelManager()
        fake = _FakeChannel()
        mgr.channels["fake"] = fake
        await fake.start(mgr._on_message)
        await mgr._on_message(InboundMessage(
            channel="fake", chat_id="123", sender_id="1",
            sender_name="Syed", text="hello",
        ))
        # "On it" ack arrives immediately
        for _ in range(20):
            if fake.sent:
                break
            await _asyncio.sleep(0.1)
        assert fake.sent and "On it" in fake.sent[0].text
        # task was created with channel source
        tasks = await runner.store.list()
        assert any(t.get("source") == "fake:123" for t in tasks)
        await mgr.stop()
    finally:
        agent_mod.override_runner(None)


def test_skill_export_import_roundtrip(client):
    c = client
    c.post("/api/skills", json={
        "name": "greeter",
        "description": "Greet warmly",
        "instructions": "1. Say hi",
        "tools": ["echo_tool"],
    })
    exported = c.get("/api/skills/greeter/export").json()
    assert exported["name"] == "greeter"
    assert exported["content"].startswith("---\n")
    assert "Say hi" in exported["content"]

    c.delete("/api/skills/greeter")
    assert c.get("/api/skills").json()["skills"] == []

    r = c.post("/api/skills/import", json={"content": exported["content"]})
    assert r.status_code == 200
    assert r.json()["name"] == "greeter"
    assert len(c.get("/api/skills").json()["skills"]) == 1


def test_skill_import_rejects_garbage(client):
    r = client.post("/api/skills/import", json={"content": "not a skill file"})
    assert r.status_code == 400


FAKE_MCP = """
import json, sys
def send(o): sys.stdout.write(json.dumps(o) + "\\n"); sys.stdout.flush()
for line in sys.stdin:
    try: msg = json.loads(line)
    except Exception: continue
    mid, method = msg.get("id"), msg.get("method")
    if method == "initialize":
        send({"jsonrpc": "2.0", "id": mid, "result": {"protocolVersion": "2024-11-05"}})
    elif method == "tools/list":
        send({"jsonrpc": "2.0", "id": mid, "result": {"tools": [
            {"name": "ping", "description": "Ping test",
             "inputSchema": {"type": "object", "properties": {"msg": {"type": "string"}}}}]}})
    elif method == "tools/call":
        send({"jsonrpc": "2.0", "id": mid,
              "result": {"content": [{"type": "text", "text": "pong:" + msg["params"]["arguments"].get("msg", "")}]}})
"""


async def test_mcp_tools_registered_with_approval(monkeypatch):
    import json as _json

    from app import mcp_setup

    monkeypatch.setattr(
        settings, "mcp_servers",
        _json.dumps({"fake": {"command": sys.executable, "args": ["-c", FAKE_MCP]}}),
    )
    registry = ToolRegistry()
    try:
        count = await mcp_setup.register_mcp_servers(registry)
        assert count == 1
        tool = registry.get("mcp_fake_ping")
        assert tool is not None
        assert tool.requires_approval is True
        assert tool.risk == "medium"
        result, _receipt = await registry.call("mcp_fake_ping", {"msg": "hello"})
        assert result.ok and result.output == "pong:hello"
    finally:
        await mcp_setup.close_mcp_servers()
        monkeypatch.setattr(settings, "mcp_servers", "")


async def test_mcp_bad_server_skipped(monkeypatch):
    import json as _json

    from app import mcp_setup

    monkeypatch.setattr(
        settings, "mcp_servers", _json.dumps({"bad": {"command": "/nonexistent/xyz"}})
    )
    registry = ToolRegistry()
    try:
        count = await mcp_setup.register_mcp_servers(registry)
    finally:
        await mcp_setup.close_mcp_servers()
    assert count == 0
