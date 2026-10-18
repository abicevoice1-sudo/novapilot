"""Minimal MCP stdio client: initialize -> tools/list -> tools/call."""

from __future__ import annotations

import asyncio
import json
import logging
from dataclasses import dataclass, field
from typing import Self

log = logging.getLogger("novapilot.mcp")

PROTOCOL_VERSION = "2024-11-05"


class MCPError(Exception):
    pass


@dataclass
class MCPTool:
    name: str
    description: str
    input_schema: dict = field(default_factory=dict)


class MCPClient:
    """One MCP server over stdio. Use as an async context manager."""

    def __init__(self, command: str, args: list[str] | None = None, env: dict | None = None) -> None:
        self.command = command
        self.args = args or []
        self.env = env
        self._proc: asyncio.subprocess.Process | None = None
        self._id = 0
        self._stderr_task: asyncio.Task | None = None

    async def __aenter__(self) -> Self:
        import os

        full_env = dict(os.environ)
        if self.env:
            full_env.update(self.env)
        try:
            self._proc = await asyncio.create_subprocess_exec(
                self.command,
                *self.args,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env=full_env,
            )
        except FileNotFoundError as e:
            raise MCPError(f"cannot start MCP server {self.command!r}: {e}") from e
        self._stderr_task = asyncio.create_task(self._drain_stderr())
        try:
            await self._initialize()
        except Exception:
            await self.__aexit__(None, None, None)
            raise
        return self

    async def __aexit__(self, *exc) -> None:
        if self._stderr_task is not None:
            self._stderr_task.cancel()
            self._stderr_task = None
        if self._proc is not None:
            try:
                self._proc.terminate()
                await asyncio.wait_for(self._proc.wait(), timeout=5)
            except (TimeoutError, ProcessLookupError):
                pass
            self._proc = None

    async def _drain_stderr(self) -> None:
        assert self._proc and self._proc.stderr
        while True:
            line = await self._proc.stderr.readline()
            if not line:
                return
            log.debug("mcp stderr: %s", line.decode(errors="replace").rstrip())

    async def _request(self, method: str, params: dict | None = None) -> dict:
        assert self._proc and self._proc.stdin and self._proc.stdout
        self._id += 1
        req = {"jsonrpc": "2.0", "id": self._id, "method": method}
        if params is not None:
            req["params"] = params
        self._proc.stdin.write((json.dumps(req) + "\n").encode())
        await self._proc.stdin.drain()
        # Read one JSON-RPC message (responses have "id"; notifications don't).
        while True:
            line = await asyncio.wait_for(self._proc.stdout.readline(), timeout=30)
            if not line:
                raise MCPError("MCP server closed stdout")
            try:
                msg = json.loads(line)
            except json.JSONDecodeError:
                continue
            if msg.get("id") == self._id:
                if "error" in msg:
                    raise MCPError(f"MCP error: {msg['error']}")
                return msg.get("result", {})
            # else: a notification or someone else's message — keep reading

    async def _notify(self, method: str) -> None:
        assert self._proc and self._proc.stdin
        self._proc.stdin.write((json.dumps({"jsonrpc": "2.0", "method": method}) + "\n").encode())
        await self._proc.stdin.drain()

    async def _initialize(self) -> None:
        result = await self._request(
            "initialize",
            {
                "protocolVersion": PROTOCOL_VERSION,
                "capabilities": {},
                "clientInfo": {"name": "novapilot", "version": "0.8.0"},
            },
        )
        server_version = result.get("protocolVersion")
        log.info("MCP server %s initialized (protocol %s)", self.command, server_version)
        await self._notify("notifications/initialized")

    async def list_tools(self) -> list[MCPTool]:
        result = await self._request("tools/list", {})
        tools = []
        for t in result.get("tools", []):
            tools.append(
                MCPTool(
                    name=t["name"],
                    description=t.get("description", ""),
                    input_schema=t.get("inputSchema", {}),
                )
            )
        return tools

    async def call_tool(self, name: str, arguments: dict) -> str:
        result = await self._request("tools/call", {"name": name, "arguments": arguments})
        parts = []
        for block in result.get("content", []):
            if block.get("type") == "text":
                parts.append(block.get("text", ""))
            else:
                parts.append(f"[{block.get('type', 'unknown')}]")
        if result.get("isError"):
            raise MCPError("MCP tool error: " + "\n".join(parts))
        return "\n".join(parts)
