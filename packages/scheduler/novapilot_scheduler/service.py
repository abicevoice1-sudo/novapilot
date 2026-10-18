"""SchedulerService: native asyncio driver over APScheduler trigger math.

Why not AsyncIOScheduler: its shutdown is fire-and-forget
(call_soon_threadsafe), which races event-loop teardown and hangs/flakes
under sequential TestClient portals. CronTrigger/IntervalTrigger are pure
fire-time calculators with no loop involvement, so we keep those and drive
them with a single cancellable asyncio task. Deterministic, test-friendly.

The service owns *runtime* jobs. Schedule definitions live in the caller's
store (the API database); on boot the caller re-registers every enabled
schedule and the service replays runs missed during downtime.
"""

from __future__ import annotations

import asyncio
import logging
from collections.abc import Awaitable, Callable
from datetime import UTC, datetime, timedelta

log = logging.getLogger("novapilot.scheduler")

MISFIRE_GRACE_SEC = 600  # a run missed by more than this gets replayed once


class SchedulerService:
    def __init__(self, fire: Callable[[object], Awaitable[None]]) -> None:
        """fire: async callback invoked with the Schedule on every trigger."""
        self._fire = fire
        self._schedules: dict[str, object] = {}
        self._task: asyncio.Task | None = None
        self._wakeup = asyncio.Event()

    # ------------------------------------------------------------ lifecycle
    async def start(self) -> None:
        if self._task is None or self._task.done():
            self._wakeup = asyncio.Event()
            self._task = asyncio.create_task(self._loop(), name="novapilot-scheduler")
            log.info("scheduler started")

    async def stop(self) -> None:
        task, self._task = self._task, None
        if task is not None and not task.done():
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
            log.info("scheduler stopped")

    # ------------------------------------------------------------ schedules
    def _trigger(self, schedule):
        from apscheduler.triggers.cron import CronTrigger
        from apscheduler.triggers.interval import IntervalTrigger

        if schedule.cron:
            return CronTrigger.from_crontab(schedule.cron)
        return IntervalTrigger(seconds=schedule.interval_sec)

    def _next_fire(self, schedule, now: datetime) -> datetime | None:
        return self._trigger(schedule).get_next_fire_time(None, now)

    def register(self, schedule) -> datetime | None:
        """(Re)register a schedule. Returns next run time. Replays missed runs.

        Missed-run detection: the caller persists next_run_at after every
        registration. If a schedule comes back with a next_run_at far in the
        past, the downtime swallowed its runs — fire once now to replay.
        """
        self._schedules[schedule.id] = schedule
        if not schedule.enabled:
            schedule.next_run_at = None
            self._wakeup.set()
            return None

        now = datetime.now(UTC)
        replay = (
            schedule.next_run_at is not None
            and schedule.next_run_at < now - timedelta(seconds=MISFIRE_GRACE_SEC)
        )
        schedule.next_run_at = self._next_fire(schedule, now)
        if replay:
            log.warning("schedule %s missed runs during downtime — replaying once", schedule.id)
            schedule.next_run_at = min(schedule.next_run_at or now, now)
        self._wakeup.set()
        return schedule.next_run_at

    def unregister(self, schedule_id: str) -> None:
        self._schedules.pop(schedule_id, None)
        self._wakeup.set()

    def next_run(self, schedule_id: str) -> datetime | None:
        s = self._schedules.get(schedule_id)
        return s.next_run_at if s is not None else None

    # ------------------------------------------------------------ driver
    async def _loop(self) -> None:
        while True:
            now = datetime.now(UTC)
            due = [
                s for s in self._schedules.values()
                if s.enabled and s.next_run_at is not None and s.next_run_at <= now
            ]
            for s in due:
                # Advance first so a slow fire can't double-trigger.
                s.next_run_at = self._next_fire(s, now + timedelta(seconds=1))
                await self._run_job(s.id)

            now = datetime.now(UTC)
            upcoming = [
                s.next_run_at for s in self._schedules.values()
                if s.enabled and s.next_run_at is not None and s.next_run_at > now
            ]
            delay = min(((nxt - now).total_seconds() for nxt in upcoming), default=None)
            self._wakeup.clear()
            try:
                if delay is None:
                    await self._wakeup.wait()
                else:
                    await asyncio.wait_for(self._wakeup.wait(), timeout=max(delay, 0))
            except TimeoutError:
                pass  # a fire time arrived; loop around and fire it

    async def _run_job(self, schedule_id: str) -> None:
        schedule = self._schedules.get(schedule_id)
        if schedule is None or not schedule.enabled:
            return
        schedule.last_run_at = datetime.now(UTC)
        schedule.run_count += 1
        log.info("schedule %s fired (run #%d)", schedule_id, schedule.run_count)
        try:
            await self._fire(schedule)
        except Exception:
            log.exception("schedule %s fire callback failed", schedule_id)
