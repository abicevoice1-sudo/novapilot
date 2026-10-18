"""MCP client tests against a fake stdio MCP server."""

import sys

import pytest

from novapilot_mcp import MCPClient, MCPError

FAKE_SERVER = """
import json, sys
def send(obj):
    sys.stdout.write(json.dumps(obj) + "\\n"); sys.stdout.flush()
tools = [{"name": "add", "description": "Add two numbers",
          "inputSchema": {"type": "object", "properties": {"a": {"type": "number"}, "b": {"type": "number"}}}}]
for line in sys.stdin:
    try:
        msg = json.loads(line)
    except Exception:
        continue
    mid, method = msg.get("id"), msg.get("method")
    if method == "initialize":
        send({"jsonrpc": "2.0", "id": mid,
              "result": {"protocolVersion": "2024-11-05", "serverInfo": {"name": "fake"}}})
    elif method == "tools/list":
        send({"jsonrpc": "2.0", "id": mid, "result": {"tools": tools}})
    elif method == "tools/call":
        a = msg["params"]["arguments"]
        if msg["params"]["name"] == "add":
            send({"jsonrpc": "2.0", "id": mid,
                  "result": {"content": [{"type": "text", "text": str(a["a"] + a["b"])}]}})
        else:
            send({"jsonrpc": "2.0", "id": mid,
                  "result": {"content": [{"type": "text", "text": "nope"}], "isError": True}})
    # notifications get no reply
"""


async def test_list_and_call():
    async with MCPClient(sys.executable, ["-c", FAKE_SERVER]) as client:
        tools = await client.list_tools()
        assert [t.name for t in tools] == ["add"]
        assert tools[0].input_schema["type"] == "object"
        assert await client.call_tool("add", {"a": 2, "b": 3}) == "5"


async def test_tool_error_raises():
    async with MCPClient(sys.executable, ["-c", FAKE_SERVER]) as client:
        with pytest.raises(MCPError):
            await client.call_tool("missing", {})


async def test_bad_command():
    with pytest.raises(MCPError):
        async with MCPClient("/nonexistent/mcp-server-xyz"):
            pass
