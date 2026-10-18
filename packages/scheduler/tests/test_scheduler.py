"""Scheduler tests: parsing, model validation, service firing + replay."""

import asyncio
from datetime import UTC, datetime, timedelta

import pytest

from novapilot_scheduler import (
    Schedule,
    ScheduleParseError,
    SchedulerService,
    parse_schedule,
)


def test_model_requires_one_trigger():
    with pytest.raises(ValueError):
        Schedule(name="x", goal="y")
    with pytest.raises(ValueError):
        Schedule(name="x", goal="y", cron="* * * * *", interval_sec=60)
    s = Schedule(name="x", goal="y", interval_sec=60)
    assert s.trigger_description() == "every 1m"


def test_parse_daily():
    assert parse_schedule("every morning at 8") == {"cron": "0 8 * * *"}
    assert parse_schedule("daily at 8:30pm") == {"cron": "30 20 * * *"}
    assert parse_schedule("every evening") == {"cron": "0 18 * * *"}
    assert parse_schedule("every day at 07:05") == {"cron": "5 7 * * *"}


def test_parse_weekdays():
    assert parse_schedule("every monday at 9am") == {"cron": "0 9 * * mon"}
    assert parse_schedule("every mon and fri at 18:00") == {"cron": "0 18 * * fri,mon"}


def test_parse_intervals():
    assert parse_schedule("every 30 minutes") == {"interval_sec": 1800}
    assert parse_schedule("every 2 hours") == {"interval_sec": 7200}
    assert parse_schedule("hourly") == {"interval_sec": 3600}


def test_parse_failures():
    with pytest.raises(ScheduleParseError):
        parse_schedule("whenever I feel like it")
    with pytest.raises(ScheduleParseError):
        parse_schedule("")
    with pytest.raises(ScheduleParseError):
        parse_schedule("every 0 minutes")


async def test_service_fires():
    fired = []

    async def fire(schedule):
        fired.append(schedule.id)

    svc = SchedulerService(fire)
    await svc.start()
    try:
        s = Schedule(name="t", goal="g", interval_sec=1)
        nxt = svc.register(s)
        assert nxt is not None
        await asyncio.sleep(2.5)
        assert fired and all(f == s.id for f in fired)
        assert s.run_count >= 1
        assert s.last_run_at is not None
    finally:
        await svc.stop()


async def test_replay_missed_run():
    fired = []

    async def fire(schedule):
        fired.append(schedule.id)

    svc = SchedulerService(fire)
    await svc.start()
    try:
        s = Schedule(
            name="t",
            goal="g",
            interval_sec=3600,
            next_run_at=datetime.now(UTC) - timedelta(hours=3),  # missed during downtime
        )
        svc.register(s)
        await asyncio.sleep(1.5)
        assert fired == [s.id]  # replayed once
    finally:
        await svc.stop()


async def test_no_replay_when_fresh():
    fired = []

    async def fire(schedule):
        fired.append(schedule.id)

    svc = SchedulerService(fire)
    await svc.start()
    try:
        s = Schedule(name="t", goal="g", interval_sec=3600)
        svc.register(s)
        await asyncio.sleep(1.0)
        assert fired == []
    finally:
        await svc.stop()


async def test_disabled_not_scheduled():
    fired = []

    async def fire(schedule):
        fired.append(schedule.id)

    svc = SchedulerService(fire)
    await svc.start()
    try:
        s = Schedule(name="t", goal="g", interval_sec=1, enabled=False)
        assert svc.register(s) is None
        await asyncio.sleep(1.5)
        assert fired == []
    finally:
        await svc.stop()
