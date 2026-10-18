"""Schedule model: exactly one of cron / interval_sec is set."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Schedule:
    name: str
    goal: str
    cron: str | None = None
    interval_sec: int | None = None
    preapproved_tools: list[str] = field(default_factory=list)
    enabled: bool = True
    id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    last_run_at: datetime | None = None
    last_task_id: str | None = None
    next_run_at: datetime | None = None
    run_count: int = 0
    created_at: datetime | None = None

    def __post_init__(self) -> None:
        if bool(self.cron) == bool(self.interval_sec):
            raise ValueError("exactly one of cron / interval_sec must be set")

    def trigger_description(self) -> str:
        if self.cron:
            return f"cron {self.cron}"
        mins, secs = divmod(self.interval_sec or 0, 60)
        hrs, mins = divmod(mins, 60)
        parts = []
        if hrs:
            parts.append(f"{hrs}h")
        if mins:
            parts.append(f"{mins}m")
        if secs or not parts:
            parts.append(f"{secs}s")
        return "every " + " ".join(parts)
