"""Multi-agent delegation: specialists with restricted toolsets.

The planner can call `delegate(role, goal)` to hand a sub-goal to a
specialist sub-agent. The sub-agent runs the same plan→execute→summarize
graph but sees only its role's tools (and can never delegate further —
no infinite recursion). It shares the parent task's approval queue and
event stream, so gates and visibility work exactly as for the parent.
"""

from __future__ import annotations

from collections.abc import Callable
from contextvars import ContextVar

from pydantic import BaseModel, Field

from .tools import Tool, ToolRegistry, ToolResult

# Current task id for the delegate tool. Set by _execute_node per step.
current_task_id: ContextVar[str | None] = ContextVar("novapilot_task_id", default=None)

# Role -> tools the specialist may use. Names must match registered tools;
# unknown names are ignored by ToolRegistry.subset().
SPECIALISTS: dict[str, dict] = {
    "researcher": {
        "description": "Gathers information: web pages, email, calendar, memory. Cannot write files or act.",
        "tools": [
            "web_fetch",
            "gmail_list",
            "gmail_read",
            "calendar_list",
            "memory_search",
            "memory_list",
        ],
    },
    "coder": {
        "description": "Reads and writes files, runs read-only shell commands. Cannot touch the browser or send email.",
        "tools": ["read_file", "list_dir", "write_file", "shell"],
    },
    "browser_operator": {
        "description": "Drives the web browser: open pages, fill forms, click, read. Cannot send email or write files.",
        "tools": [
            "browser_open",
            "browser_fill",
            "browser_click",
            "browser_read",
            "browser_screenshot",
            "browser_back",
            "browser_snapshot",
        ],
    },
    "communicator": {
        "description": "Sends email and manages the calendar. Every send/create needs approval.",
        "tools": ["gmail_list", "gmail_read", "gmail_send", "calendar_list", "calendar_create"],
    },
}


class _DelegateArgs(BaseModel):
    role: str = Field(description=f"Specialist role: {', '.join(SPECIALISTS)}")
    goal: str = Field(description="Sub-goal for the specialist, self-contained")


def register_delegate_tool(
    registry: ToolRegistry,
    run_subtask: Callable[[str, str], object],
) -> None:
    """Register the `delegate` tool.

    run_subtask(role, goal) runs the specialist and returns its summary
    (awaitable). Provided by the TaskRunner; see runner.run_delegate.
    """

    async def _delegate(args: _DelegateArgs) -> ToolResult:
        role = args.role.strip().lower()
        if role not in SPECIALISTS:
            return ToolResult(
                ok=False,
                output=f"unknown role {args.role!r}; choose from: {', '.join(SPECIALISTS)}",
            )
        try:
            summary = await run_subtask(role, args.goal)
        except Exception as e:  # noqa: BLE001 — delegation failure is a tool error, not a crash
            return ToolResult(ok=False, output=f"specialist failed: {e}")
        return ToolResult(
            ok=True,
            output=f"[specialist:{role}] {summary}",
            verification=f"delegated to {role}",
        )

    registry.register(
        Tool(
            "delegate",
            "Hand a sub-goal to a specialist sub-agent (researcher, coder, "
            "browser_operator, communicator). Returns the specialist's summary.",
            _DelegateArgs,
            _delegate,
        )
    )
