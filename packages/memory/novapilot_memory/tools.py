"""Agent tool bindings for memory: search/add/update are low-risk, delete needs approval."""

from __future__ import annotations

from collections.abc import Callable

from pydantic import BaseModel, Field

from .service import MemoryService


class _SearchArgs(BaseModel):
    query: str = Field(description="What to recall")
    limit: int = Field(default=5, le=20)


class _AddArgs(BaseModel):
    content: str = Field(description="The fact to remember")
    tags: list[str] = Field(default_factory=list)


class _UpdateArgs(BaseModel):
    id: str = Field(description="Memory id")
    content: str | None = None
    tags: list[str] | None = None


class _DeleteArgs(BaseModel):
    id: str = Field(description="Memory id to forget")


def register_memory_tools(registry, service: MemoryService, namespace_fn: Callable[[], str]):
    """Register memory_* tools on an agent-core ToolRegistry."""
    from novapilot_agent.tools import Tool, ToolResult

    async def _search(args: _SearchArgs) -> ToolResult:
        hits = await service.recall(namespace_fn(), args.query, limit=args.limit)
        if not hits:
            return ToolResult(ok=True, output="no memories found", verification="searched")
        out = "\n".join(f"- [{h['id']}] {h['content']}" for h in hits)
        return ToolResult(ok=True, output=out, verification=f"recalled {len(hits)}")

    async def _add(args: _AddArgs) -> ToolResult:
        try:
            result = await service.remember(namespace_fn(), args.content, tags=args.tags, source="agent")
        except ValueError as e:
            return ToolResult(ok=False, output=str(e))
        m = result["memory"]
        return ToolResult(
            ok=True,
            output=f"remembered [{m['id']}]" + (" (merged with existing)" if result["merged"] else ""),
            verification="stored",
        )

    async def _update(args: _UpdateArgs) -> ToolResult:
        try:
            updated = await service.update_memory(args.id, content=args.content, tags=args.tags)
        except ValueError as e:
            return ToolResult(ok=False, output=str(e))
        if updated is None:
            return ToolResult(ok=False, output=f"unknown memory: {args.id}")
        return ToolResult(ok=True, output=f"updated [{args.id}]", verification="stored")

    async def _delete(args: _DeleteArgs) -> ToolResult:
        ok = await service.forget(args.id)
        return ToolResult(
            ok=ok,
            output=f"forgot [{args.id}]" if ok else f"unknown memory: {args.id}",
            verification="deleted from store",
        )

    registry.register(Tool("memory_search", "Search the user's long-term memory", _SearchArgs, _search))
    registry.register(Tool("memory_add", "Save a durable fact to memory", _AddArgs, _add))
    registry.register(Tool("memory_update", "Update a memory by id", _UpdateArgs, _update))
    registry.register(
        Tool(
            "memory_delete",
            "Permanently forget a memory by id (needs approval)",
            _DeleteArgs,
            _delete,
            risk="medium",
            requires_approval=True,
        )
    )
