"""Memory endpoints: the user owns this data — read everything, edit, delete."""

from __future__ import annotations

import json

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from ..auth import require_auth
from ..config import settings
from ..memory import get_memory_service

router = APIRouter()

EXTRACT_PROMPT = """Extract durable facts about the user from this conversation.
Durable = preferences, decisions, names, dates, goals, constraints — things worth
remembering next week. Skip trivia, small talk, and anything already obvious.
Return ONLY a JSON array. Each item: {"content": "...", "tags": ["..."]}.
If nothing is worth remembering, return []."""


class AddMemoryRequest(BaseModel):
    content: str = Field(max_length=20000)
    tags: list[str] = Field(default=[], max_length=50)


class UpdateMemoryRequest(BaseModel):
    content: str | None = Field(default=None, max_length=20000)
    tags: list[str] | None = Field(default=None, max_length=50)


class ImportRequest(BaseModel):
    memories: list[dict] = Field(max_length=5000)


@router.get("/api/memories", dependencies=[Depends(require_auth)])
async def list_memories(q: str | None = None, limit: int = 50, offset: int = 0):
    svc = await get_memory_service()
    ns = settings.memory_namespace
    if q:
        hits = await svc.recall(ns, q, limit=limit)
        return {"memories": hits, "total": len(hits), "query": q}
    memories, total = await svc.list_memories(ns, limit=min(limit, 200), offset=offset)
    return {"memories": memories, "total": total}


@router.post("/api/memories", dependencies=[Depends(require_auth)])
async def add_memory(req: AddMemoryRequest):
    svc = await get_memory_service()
    try:
        result = await svc.remember(settings.memory_namespace, req.content, tags=req.tags)
    except ValueError as e:
        raise HTTPException(400, str(e)) from e
    return result


@router.get("/api/memories/export", dependencies=[Depends(require_auth)])
async def export_memories():
    svc = await get_memory_service()
    return {"memories": await svc.export(settings.memory_namespace)}


@router.post("/api/memories/import", dependencies=[Depends(require_auth)])
async def import_memories(req: ImportRequest):
    svc = await get_memory_service()
    return await svc.import_memories(settings.memory_namespace, req.memories)


@router.get("/api/memories/{mid}", dependencies=[Depends(require_auth)])
async def get_memory(mid: str):
    svc = await get_memory_service()
    memory = await svc.store.get(mid)
    if memory is None or memory["namespace"] != settings.memory_namespace:
        raise HTTPException(404, "memory not found")
    return memory


@router.patch("/api/memories/{mid}", dependencies=[Depends(require_auth)])
async def update_memory(mid: str, req: UpdateMemoryRequest):
    svc = await get_memory_service()
    existing = await svc.store.get(mid)
    if existing is None or existing["namespace"] != settings.memory_namespace:
        raise HTTPException(404, "memory not found")
    try:
        updated = await svc.update_memory(mid, content=req.content, tags=req.tags)
    except ValueError as e:
        raise HTTPException(400, str(e)) from e
    return updated


@router.delete("/api/memories/{mid}", dependencies=[Depends(require_auth)])
async def delete_memory(mid: str):
    svc = await get_memory_service()
    existing = await svc.store.get(mid)
    if existing is None or existing["namespace"] != settings.memory_namespace:
        raise HTTPException(404, "memory not found")
    await svc.forget(mid)
    return {"deleted": mid}


@router.post(
    "/api/conversations/{conv_id}/extract-memories", dependencies=[Depends(require_auth)]
)
async def extract_memories(conv_id: str):
    """Consented write path: the user asks Actlet to remember this conversation."""
    from ..db import Message, SessionLocal
    from ..gateway_dep import get_gateway

    async with SessionLocal() as s:
        from sqlalchemy import select

        rows = (
            (await s.execute(select(Message).where(Message.conversation_id == conv_id).order_by(Message.id)))
            .scalars()
            .all()
        )
    if not rows:
        raise HTTPException(404, "conversation not found or empty")
    transcript = "\n".join(f"{m.role}: {m.content[:500]}" for m in rows[-20:])

    gateway = get_gateway()
    try:
        raw = await gateway.chat(
            [
                {"role": "system", "content": "You output only JSON."},
                {"role": "user", "content": EXTRACT_PROMPT + "\n\nCONVERSATION:\n" + transcript},
            ]
        )
    except Exception as e:
        raise HTTPException(502, f"extraction needs a reachable model: {e}") from e


    try:
        text = raw.strip()
        if text.startswith("```"):
            text = text.split("\n", 1)[1].rsplit("```", 1)[0]
        items = json.loads(text)
        assert isinstance(items, list)
    except Exception as e:
        raise HTTPException(502, f"could not parse extracted memories: {e}") from e

    svc = await get_memory_service()
    added = []
    for item in items:
        if not isinstance(item, dict) or not (item.get("content") or "").strip():
            continue
        try:
            result = await svc.remember(
                settings.memory_namespace,
                item["content"],
                tags=item.get("tags") or [],
                source="extract",
            )
            added.append(result["memory"])
        except ValueError:
            continue
    return {"added": added, "count": len(added)}


def build_memory_context(hits: list[dict]) -> str:
    lines = "\n".join(f"- {h['content']}" for h in hits)
    return f"Relevant memories about the user (from Actlet's long-term memory):\n{lines}"
