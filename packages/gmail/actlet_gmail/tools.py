"""Agent tools for Gmail: read (low risk), send (high risk + approval)."""

from __future__ import annotations

import asyncio
from collections.abc import Callable

from actlet_agent.tools import Tool, ToolRegistry, ToolResult
from pydantic import BaseModel, Field

from .client import GmailClient


class _ListArgs(BaseModel):
    folder: str = Field(default="INBOX")
    limit: int = Field(default=10, ge=1, le=50)
    unread_only: bool = Field(default=False)


class _ReadArgs(BaseModel):
    uid: str = Field(description="Message UID from gmail_list")
    folder: str = Field(default="INBOX")


class _SendArgs(BaseModel):
    to: str = Field(description="Recipient email address")
    subject: str = Field(description="Subject line")
    body: str = Field(description="Plain-text body")


def register_gmail_tools(
    registry: ToolRegistry, client_factory: Callable[[], GmailClient]
) -> None:
    async def _list(args: _ListArgs) -> ToolResult:
        client = client_factory()
        msgs = await asyncio.to_thread(
            client.list_messages, args.folder, args.limit, args.unread_only
        )
        lines = [
            f"[{m.uid}] {'UNREAD ' if m.unread else ''}{m.date} | {m.from_addr} | {m.subject}"
            for m in msgs
        ]
        return ToolResult(
            ok=True,
            output="\n".join(lines) if lines else "(no messages)",
            verification=f"{len(msgs)} messages listed",
        )

    async def _read(args: _ReadArgs) -> ToolResult:
        client = client_factory()
        m = await asyncio.to_thread(client.read_message, args.uid, args.folder)
        return ToolResult(
            ok=True,
            output=f"From: {m.from_addr}\nTo: {m.to_addr}\nDate: {m.date}\n"
            f"Subject: {m.subject}\n\n{m.body}",
            verification=f"read message {m.uid}",
        )

    async def _send(args: _SendArgs) -> ToolResult:
        client = client_factory()
        await asyncio.to_thread(client.send, args.to, args.subject, args.body)
        return ToolResult(
            ok=True,
            output=f"sent to {args.to}",
            verification=f"email sent to {args.to}",
        )

    registry.register(
        Tool("gmail_list", "List recent Gmail messages (headers only)", _ListArgs, _list)
    )
    registry.register(
        Tool("gmail_read", "Read a Gmail message body by UID", _ReadArgs, _read)
    )
    registry.register(
        Tool(
            "gmail_send",
            "Send an email via Gmail (needs approval)",
            _SendArgs,
            _send,
            risk="high",
            requires_approval=True,
        )
    )
