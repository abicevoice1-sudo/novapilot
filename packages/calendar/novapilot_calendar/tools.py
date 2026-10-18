"""Agent tools: calendar_list (low risk), calendar_create (high risk + approval)."""

from __future__ import annotations

import asyncio
from collections.abc import Callable

from novapilot_agent.tools import Tool, ToolRegistry, ToolResult
from pydantic import BaseModel, Field

from .client import CalendarClient


class _ListArgs(BaseModel):
    days: int = Field(default=7, ge=1, le=60, description="How many days ahead to look")


class _CreateArgs(BaseModel):
    summary: str = Field(description="Event title")
    start_iso: str = Field(description="Start, ISO 8601 (e.g. 2026-10-19T14:00:00)")
    end_iso: str = Field(description="End, ISO 8601")
    description: str = Field(default="")
    location: str = Field(default="")


def register_calendar_tools(
    registry: ToolRegistry, client_factory: Callable[[], CalendarClient]
) -> None:
    async def _list(args: _ListArgs) -> ToolResult:
        client = client_factory()
        events = await asyncio.to_thread(client.list_events, args.days)
        lines = [
            f"{e.start} → {e.end} | {e.summary}" + (f" @ {e.location}" if e.location else "")
            for e in events
        ]
        return ToolResult(
            ok=True,
            output="\n".join(lines) if lines else "(no upcoming events)",
            verification=f"{len(events)} events listed",
        )

    async def _create(args: _CreateArgs) -> ToolResult:
        client = client_factory()
        try:
            summary = await asyncio.to_thread(
                client.create_event,
                args.summary,
                args.start_iso,
                args.end_iso,
                args.description,
                args.location,
            )
        except ValueError as e:
            return ToolResult(ok=False, output=f"bad date: {e}")
        return ToolResult(
            ok=True,
            output=f"created: {summary}",
            verification=f"calendar event created: {summary}",
        )

    registry.register(
        Tool("calendar_list", "List upcoming calendar events", _ListArgs, _list)
    )
    registry.register(
        Tool(
            "calendar_create",
            "Create a calendar event (needs approval)",
            _CreateArgs,
            _create,
            risk="high",
            requires_approval=True,
        )
    )
