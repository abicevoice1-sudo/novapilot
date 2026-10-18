"""SQLAlchemy implementation of the agent-core TaskStore protocol."""

from __future__ import annotations

import json
import uuid

from .db import SessionLocal, Task, TaskEvent


class SqlTaskStore:
    def __init__(self, session_factory=SessionLocal) -> None:
        self._sessions = session_factory

    async def create(self, goal: str, model: str | None, thread_id: str, source: str | None = None) -> str:
        tid = uuid.uuid4().hex[:12]
        async with self._sessions() as s:
            s.add(Task(id=tid, goal=goal, model=model, status="pending", thread_id=thread_id, source=source))
            await s.commit()
        return tid

    async def update(self, task_id: str, **fields) -> None:
        async with self._sessions() as s:
            task = await s.get(Task, task_id)
            if task is None:
                return
            for k, v in fields.items():
                setattr(task, k, v)
            await s.commit()

    async def get(self, task_id: str) -> dict | None:
        async with self._sessions() as s:
            task = await s.get(Task, task_id)
            return self._to_dict(task) if task else None

    async def list(self, limit: int = 50) -> list[dict]:
        from sqlalchemy import desc, select

        async with self._sessions() as s:
            rows = (
                (await s.execute(select(Task).order_by(desc(Task.created_at)).limit(limit)))
                .scalars()
                .all()
            )
            return [self._to_dict(t) for t in rows]

    async def add_event(self, task_id: str, type: str, payload: dict) -> None:
        async with self._sessions() as s:
            s.add(TaskEvent(task_id=task_id, type=type, payload_json=json.dumps(payload)))
            await s.commit()

    async def events(self, task_id: str, after_id: int = 0) -> list[dict]:
        from sqlalchemy import select

        async with self._sessions() as s:
            rows = (
                (
                    await s.execute(
                        select(TaskEvent)
                        .where(TaskEvent.task_id == task_id, TaskEvent.id > after_id)
                        .order_by(TaskEvent.id)
                    )
                )
                .scalars()
                .all()
            )
            out = []
            for r in rows:
                p = json.loads(r.payload_json)
                # runner-assigned seq is canonical (survives restarts); row id is fallback
                out.append({"seq": p.get("seq", r.id), "type": r.type, **p})
            return out

    @staticmethod
    def _to_dict(t: Task) -> dict:
        return {
            "id": t.id,
            "goal": t.goal,
            "model": t.model,
            "status": t.status,
            "thread_id": t.thread_id,
            "current_step": t.current_step,
            "total_steps": t.total_steps,
            "error": t.error,
            "summary": t.summary,
            "usage": json.loads(t.usage_json or "{}"),
            "created_at": t.created_at.isoformat() if t.created_at else None,
            "updated_at": t.updated_at.isoformat() if t.updated_at else None,
        }
