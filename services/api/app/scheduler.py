"""Scheduler singleton: APScheduler service + DB-backed schedule definitions.

Fire path: schedule triggers -> TaskRunner.create_task with the schedule's
explicit pre-approved tools (default: none — fully supervised) and
source="schedule:<id>" attribution. Missed runs during downtime are replayed
once on boot.
"""

from __future__ import annotations

import json
import logging
from datetime import UTC, datetime

from novapilot_scheduler import Schedule, SchedulerService
from sqlalchemy import select

from .config import settings  # noqa: F401  (keeps module import side-effect free)
from .db import Schedule as ScheduleRow
from .db import SessionLocal

log = logging.getLogger("novapilot.scheduler")

_service: SchedulerService | None = None


def _aware(dt: datetime | None) -> datetime | None:
    # SQLite returns naive datetimes; treat them as UTC.
    if dt is not None and dt.tzinfo is None:
        return dt.replace(tzinfo=UTC)
    return dt


def _to_model(row: ScheduleRow) -> Schedule:
    return Schedule(
        id=row.id,
        name=row.name,
        goal=row.goal,
        cron=row.cron,
        interval_sec=row.interval_sec,
        preapproved_tools=json.loads(row.preapproved_tools_json or "[]"),
        enabled=row.enabled,
        last_run_at=_aware(row.last_run_at),
        last_task_id=row.last_task_id,
        next_run_at=_aware(row.next_run_at),
        run_count=row.run_count,
        created_at=_aware(row.created_at),
    )


def _serialize(row: ScheduleRow) -> dict:
    model = _to_model(row)
    return {
        "id": row.id,
        "name": row.name,
        "goal": row.goal,
        "cron": row.cron,
        "interval_sec": row.interval_sec,
        "when": model.trigger_description(),
        "preapproved_tools": model.preapproved_tools,
        "enabled": row.enabled,
        "last_run_at": row.last_run_at.isoformat() if row.last_run_at else None,
        "last_task_id": row.last_task_id,
        "next_run_at": row.next_run_at.isoformat() if row.next_run_at else None,
        "run_count": row.run_count,
        "created_at": row.created_at.isoformat() if row.created_at else None,
    }


async def _fire(schedule: Schedule) -> None:
    from .agent import get_runner

    log.info("schedule %s firing -> task (preapproved=%s)", schedule.id, schedule.preapproved_tools)
    task_id = await get_runner().create_task(
        schedule.goal,
        preapproved_tools=schedule.preapproved_tools,
        source=f"schedule:{schedule.id}",
    )
    schedule.last_task_id = task_id
    async with SessionLocal() as s:
        row = await s.get(ScheduleRow, schedule.id)
        if row is not None:
            row.last_run_at = datetime.now(UTC)
            row.last_task_id = task_id
            row.run_count = schedule.run_count
            row.next_run_at = schedule.next_run_at
            await s.commit()


async def fire_schedule_now(schedule: Schedule) -> None:
    """Manual run-now: same accounting as a triggered fire."""
    schedule.run_count += 1
    await _fire(schedule)


def get_scheduler() -> SchedulerService:
    if _service is None:
        raise RuntimeError("scheduler not started (lifespan starts it)")
    return _service


async def start_scheduler() -> None:
    global _service
    _service = SchedulerService(_fire)
    await _service.start()
    # Reload enabled schedules from the DB; missed runs replay once.
    async with SessionLocal() as s:
        rows = (await s.execute(select(ScheduleRow).where(ScheduleRow.enabled.is_(True)))).scalars().all()
        for row in rows:
            model = _to_model(row)
            nxt = _service.register(model)
            row.next_run_at = nxt
        await s.commit()
    log.info("scheduler loaded %d enabled schedule(s)", len(rows))


async def stop_scheduler() -> None:
    global _service
    if _service is not None:
        await _service.stop()
        _service = None


async def refresh_schedule(row: ScheduleRow) -> datetime | None:
    """(Re)register a DB row with the running service; persists next_run_at."""
    model = _to_model(row)
    nxt = get_scheduler().register(model)
    row.next_run_at = nxt
    return nxt
