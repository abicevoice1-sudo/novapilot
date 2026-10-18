"""Actlet MCP client: MCP servers become agent tools.

Minimal, dependency-free JSON-RPC 2.0 over stdio: initialize handshake,
tools/list, tools/call. MCP tools are registered with risk="medium" and
require approval — external code runs outside our audit boundary.
"""

from .client import MCPClient, MCPError, MCPTool

__all__ = ["MCPClient", "MCPError", "MCPTool"]
