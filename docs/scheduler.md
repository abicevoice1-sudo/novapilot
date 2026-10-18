# Scheduler — recurring agent tasks

Schedules run agent tasks on a cadence: "every morning at 8, brief me on the
news." Each run is a normal task with the full approval machinery.

## Autonomy model (explicit, not ambient)

A schedule declares `preapproved_tools`: the exact tools it may use without
asking. **Default is empty — fully supervised.** A scheduled task that reaches
for anything else pauses at the approval gate exactly like a manual task.

Every pre-approval skip is audit-logged (`approval_decided` with
`preapproved: true`), and every task carries `source: "schedule:<id>"` so you
can always tell what ran and why.

## Triggers

One of: natural language (`when: "every morning at 8"`, `"every monday at 9am"`,
`"every 30 minutes"`, `"hourly"`), a cron string, or `interval_sec`.
Unparseable input is rejected with an honest 422 — never a guessed cron.

## Reliability

- Missed runs during downtime are replayed once on boot (persisted
  `next_run_at`; grace period 10 minutes).
- The driver is a single native asyncio task (no APScheduler event-loop
  games); a failing fire callback is logged, never kills the scheduler.
- `POST /api/schedules/{id}/run-now` fires immediately without changing cadence.
