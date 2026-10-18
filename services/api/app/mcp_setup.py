"""MCP servers -> agent tools. Configured via MCP_SERVERS env JSON:

    {"fs": {"command": "npx", "args": ["-y", "@modelcontextprotocol/server-filesystem", "/tmp"]}}

MCP tools register with risk="medium" + requires_approval=True: external code
runs outside our audit boundary, so every call needs a human yes.
"""

from __future__ import annotations

import json
import logging
from typing import Any

from novapilot_mcp import MCPClient, MCPError
from pydantic import BaseModel, ConfigDict, create_model

from .config import settings

log = logging.getLogger("novapilot.mcp")

_clients: list[MCPClient] = []


class _MCPArgs(BaseModel):
    model_config = ConfigDict(extra="allow")


def _parse_config() -> dict:
    raw = (settings.mcp_servers or "").strip()
    if not raw:
        return {}
    try:
        data = json.loads(raw)
        assert isinstance(data, dict)
        return data
    except Exception as e:  # noqa: BLE001
        log.error("MCP_SERVERS is not valid JSON: %s", e)
        return {}


def _schema_model(tool) -> type[BaseModel]:
    """Dynamic pydantic model from the MCP input schema (all-optional passthrough)."""
    props = (tool.input_schema or {}).get("properties", {}) or {}
    fields = {name: (Any | None, None) for name in props}
    return create_model(f"MCP_{tool.name}", __base__=_MCPArgs, **fields)


async def register_mcp_servers(registry) -> int:
    """Spawn configured MCP servers and register their tools. Returns tool count."""
    from novapilot_agent.tools import Tool, ToolResult

    count = 0
    for server_name, cfg in _parse_config().items():
        command = (cfg or {}).get("command")
        if not command:
            log.warning("MCP server %r has no command; skipping", server_name)
            continue
        client = MCPClient(command, args=(cfg or {}).get("args") or [])
        try:
            await client.__aenter__()
        except MCPError as e:
            log.error("MCP server %r failed to start: %s", server_name, e)
            continue
        _clients.append(client)
        try:
            tools = await client.list_tools()
        except MCPError as e:
            log.error("MCP server %r tools/list failed: %s", server_name, e)
            continue
        for t in tools:
            tool_name = f"mcp_{server_name}_{t.name}".replace("-", "_")

            def make_func(client: MCPClient, tool_name: str):
                async def _call(args: BaseModel) -> ToolResult:
                    try:
                        out = await client.call_tool(
                            tool_name, args.model_dump(exclude_none=True)
                        )
                        return ToolResult(ok=True, output=out)
                    except MCPError as e:
                        return ToolResult(ok=False, output=f"MCP error: {e}")

                return _call

            registry.register(
                Tool(
                    name=tool_name,
                    description=f"[MCP:{server_name}] {t.description or t.name}",
                    args_schema=_schema_model(t),
                    func=make_func(client, t.name),
                    risk="medium",
                    requires_approval=True,
                )
            )
            count += 1
        log.info("MCP server %r: registered %d tools", server_name, len(tools))
    return count


async def close_mcp_servers() -> None:
    while _clients:
        client = _clients.pop()
        try:
            await client.__aexit__(None, None, None)
        except Exception:
            log.exception("MCP client close failed")
