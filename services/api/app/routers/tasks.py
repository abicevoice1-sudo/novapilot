"""Task endpoints: create, list, detail, live events (SSE), approve/cancel/pause/resume."""

from __future__ import annotations

import asyncio
import json

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from ..agent import get_runner
from ..auth import require_auth

router = APIRouter()

TERMINAL_EVENTS = {"task_completed", "task_failed", "task_cancelled"}


class CreateTaskRequest(BaseModel):
    goal: str = Field(min_length=1, max_length=20000)
    model: str | None = Field(default=None, max_length=200)


class ApproveRequest(BaseModel):
    approved: bool


def _serialize(task: dict) -> dict:
    return {
        "id": task["id"],
        "goal": task["goal"],
        "status": task["status"],
        "model": task.get("model"),
        "current_step": task.get("current_step", 0),
        "total_steps": task.get("total_steps", 0),
        "error": task.get("error"),
        "usage": task.get("usage", {}),
        "created_at": task.get("created_at"),
        "updated_at": task.get("updated_at"),
    }


@router.post("/api/tasks", dependencies=[Depends(require_auth)])
async def create_task(req: CreateTaskRequest):
    if not req.goal.strip():
        raise HTTPException(400, "goal is required")
    task_id = await get_runner().create_task(req.goal.strip(), req.model)
    return {"id": task_id, "status": "running"}


@router.get("/api/tasks", dependencies=[Depends(require_auth)])
async def list_tasks():
    tasks = await get_runner().store.list()
    return {"tasks": [_serialize(t) for t in tasks]}


@router.get("/api/tasks/{task_id}", dependencies=[Depends(require_auth)])
async def get_task(task_id: str):
    state = await get_runner().get_state(task_id)
    if state is None:
        raise HTTPException(404, "task not found")
    out = _serialize(state)
    out["steps"] = [
        {
            "id": s["id"],
            "description": s["description"],
            "tool": s["tool"],
            "args": s["args"],
            "status": s["status"],
            "result": s.get("result"),
            "attempts": s.get("attempts", 0),
        }
        for s in state.get("plan", [])
    ]
    out["summary"] = state.get("summary")
    # Surface the pending approval (if any) so a reloaded page can render the
    # approval card without waiting for a live event.
    out["pending_approval"] = None
    if state["status"] == "waiting_approval":
        for e in reversed(await get_runner().store.events(task_id)):
            if e["type"] == "approval_required":
                out["pending_approval"] = e.get("step")
                break
    return out


@router.get("/api/tasks/{task_id}/events", dependencies=[Depends(require_auth)])
async def task_events(task_id: str, request: Request):
    runner = get_runner()
    if await runner.store.get(task_id) is None:
        raise HTTPException(404, "task not found")
    queue = runner.subscribe(task_id)
    history = await runner.store.events(task_id)

    async def gen():
        last_seq = 0
        for e in history:
            last_seq = max(last_seq, e.get("seq", 0))
            yield f"data: {json.dumps(e)}\n\n"
            if e["type"] in TERMINAL_EVENTS:
                return  # replayed a finished task: close the stream
        while True:
            if await request.is_disconnected():
                break
            try:
                event = await asyncio.wait_for(queue.get(), timeout=20)
            except TimeoutError:
                yield ": ping\n\n"
                continue
            if event.get("seq", 0) <= last_seq:
                continue  # already replayed from history
            last_seq = event["seq"]
            yield f"data: {json.dumps(event)}\n\n"
            if event["type"] in TERMINAL_EVENTS:
                break

    return StreamingResponse(gen(), media_type="text/event-stream")


@router.post("/api/tasks/{task_id}/approve", dependencies=[Depends(require_auth)])
async def approve_task(task_id: str, req: ApproveRequest):
    try:
        await get_runner().approve(task_id, req.approved)
    except ValueError as e:
        raise HTTPException(409, str(e)) from e
    return {"status": "running"}


@router.post("/api/tasks/{task_id}/cancel", dependencies=[Depends(require_auth)])
async def cancel_task(task_id: str):
    try:
        await get_runner().cancel(task_id)
    except ValueError as e:
        raise HTTPException(404, str(e)) from e
    return {"status": "cancelled"}


@router.post("/api/tasks/{task_id}/pause", dependencies=[Depends(require_auth)])
async def pause_task(task_id: str):
    await get_runner().pause(task_id)
    return {"status": "paused"}


@router.post("/api/tasks/{task_id}/resume", dependencies=[Depends(require_auth)])
async def resume_task(task_id: str):
    try:
        await get_runner().resume(task_id)
    except ValueError as e:
        raise HTTPException(409, str(e)) from e
    return {"status": "running"}


@router.post("/api/tasks/{task_id}/revert", dependencies=[Depends(require_auth)])
async def revert_task(task_id: str):
    """Restore the workspace to the latest pre-step checkpoint (Time Travel)."""
    from ..agent import get_checkpoint_manager

    task = await get_runner().get_state(task_id)
    if task is None:
        raise HTTPException(404, "task not found")
    mgr = get_checkpoint_manager()
    step_id = mgr.latest(task_id)
    if step_id is None:
        raise HTTPException(404, "no checkpoints for this task")
    try:
        mgr.restore(task_id, step_id)
    except ValueError as e:
        raise HTTPException(404, str(e)) from e
    return {"reverted_to": step_id}
