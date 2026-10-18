"""Schedule endpoints: CRUD, enable/disable, run-now."""

import json
from datetime import UTC, datetime

from actlet_scheduler import ScheduleParseError, parse_schedule
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select

from ..auth import require_auth
from ..db import Schedule as ScheduleRow
from ..db import SessionLocal
from ..scheduler import _serialize, get_scheduler, refresh_schedule

router = APIRouter(prefix="/api/schedules", tags=["schedules"])


class ScheduleCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    goal: str = Field(min_length=1, description="What the agent should do each run")
    # One of: when (natural language), cron, interval_sec.
    when: str | None = Field(default=None, description="'every morning at 8', 'every 30 minutes', ...")
    cron: str | None = None
    interval_sec: int | None = Field(default=None, gt=0)
    preapproved_tools: list[str] = Field(
        default_factory=list,
        description="Tools this schedule may use without asking. Empty = fully supervised.",
    )


class ScheduleUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=200)
    goal: str | None = Field(default=None, min_length=1)
    when: str | None = None
    cron: str | None = None
    interval_sec: int | None = Field(default=None, gt=0)
    preapproved_tools: list[str] | None = None
    enabled: bool | None = None


def _trigger_kwargs(data: dict) -> dict:
    """Resolve when/cron/interval_sec into exactly one trigger. Raises 400/422."""
    when, cron, interval = data.get("when"), data.get("cron"), data.get("interval_sec")
    provided = [bool(when), bool(cron), bool(interval)]
    if sum(provided) == 0:
        raise HTTPException(400, "provide one of: when, cron, interval_sec")
    if sum(provided) > 1:
        raise HTTPException(400, "provide only one of: when, cron, interval_sec")
    if when:
        try:
            return parse_schedule(when)
        except ScheduleParseError as e:
            raise HTTPException(422, str(e)) from e
    if cron:
        parts = cron.split()
        if len(parts) != 5:
            raise HTTPException(422, "cron must have 5 fields (minute hour day month weekday)")
        return {"cron": cron}
    return {"interval_sec": interval}


@router.get("", dependencies=[Depends(require_auth)])
async def list_schedules():
    async with SessionLocal() as s:
        rows = (await s.execute(select(ScheduleRow).order_by(ScheduleRow.created_at))).scalars().all()
        return {"schedules": [_serialize(r) for r in rows]}


@router.post("", dependencies=[Depends(require_auth)])
async def create_schedule(req: ScheduleCreate):
    trigger = _trigger_kwargs(req.model_dump())
    async with SessionLocal() as s:
        row = ScheduleRow(
            name=req.name.strip(),
            goal=req.goal.strip(),
            preapproved_tools_json=json.dumps(req.preapproved_tools),
            **trigger,
        )
        s.add(row)
        await s.commit()
        await s.refresh(row)
        await refresh_schedule(row)
        await s.commit()
        return _serialize(row)


@router.get("/{sid}", dependencies=[Depends(require_auth)])
async def get_schedule(sid: str):
    async with SessionLocal() as s:
        row = await s.get(ScheduleRow, sid)
        if row is None:
            raise HTTPException(404, "schedule not found")
        return _serialize(row)


@router.patch("/{sid}", dependencies=[Depends(require_auth)])
async def update_schedule(sid: str, req: ScheduleUpdate):
    data = req.model_dump(exclude_unset=True)
    async with SessionLocal() as s:
        row = await s.get(ScheduleRow, sid)
        if row is None:
            raise HTTPException(404, "schedule not found")
        trig_keys = {"when", "cron", "interval_sec"}
        if trig_keys & data.keys():
            trig_input = {k: data.pop(k, None) for k in trig_keys}
            trig = _trigger_kwargs(trig_input)
            row.cron, row.interval_sec = trig.get("cron"), trig.get("interval_sec")
        if "name" in data:
            row.name = data["name"].strip()
        if "goal" in data:
            row.goal = data["goal"].strip()
        if "preapproved_tools" in data:
            row.preapproved_tools_json = json.dumps(data["preapproved_tools"] or [])
        if "enabled" in data:
            row.enabled = data["enabled"]
        row.updated_at = datetime.now(UTC)
        await refresh_schedule(row)
        await s.commit()
        return _serialize(row)


@router.delete("/{sid}", dependencies=[Depends(require_auth)])
async def delete_schedule(sid: str):
    async with SessionLocal() as s:
        row = await s.get(ScheduleRow, sid)
        if row is None:
            raise HTTPException(404, "schedule not found")
        get_scheduler().unregister(sid)
        await s.delete(row)
        await s.commit()
        return {"deleted": sid}


@router.post("/{sid}/run-now", dependencies=[Depends(require_auth)])
async def run_schedule_now(sid: str):
    """Fire a schedule immediately (counts as a run; does not change its cadence)."""
    from ..scheduler import _to_model, fire_schedule_now

    async with SessionLocal() as s:
        row = await s.get(ScheduleRow, sid)
        if row is None:
            raise HTTPException(404, "schedule not found")
        model = _to_model(row)
        await fire_schedule_now(model)
        await s.commit()
        await s.refresh(row)
        return {"fired": sid, "task_id": row.last_task_id}
