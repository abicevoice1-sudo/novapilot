"""Global agent control: pause/resume + quiet hours.

Pause is a runtime flag (no restart needed): while paused, the scheduler
skips firing and channels stop creating tasks. Run-now still works —
the user explicitly asked.
"""

from __future__ import annotations

from datetime import datetime

from .config import settings

_paused: bool = False


def is_paused() -> bool:
    return _paused


def set_paused(value: bool) -> None:
    global _paused
    _paused = value


def _parse_hhmm(value: str) -> tuple[int, int] | None:
    try:
        h, m = value.split(":")
        h_i, m_i = int(h), int(m)
        if 0 <= h_i < 24 and 0 <= m_i < 60:
            return h_i, m_i
    except (ValueError, AttributeError):
        pass
    return None


def in_quiet_hours(now: datetime | None = None) -> bool:
    """True if the current local time falls inside the quiet-hours window."""
    start = _parse_hhmm(settings.quiet_hours_start)
    end = _parse_hhmm(settings.quiet_hours_end)
    if not start or not end:
        return False
    now = now or datetime.now().astimezone()
    cur = (now.hour, now.minute)
    if start <= end:
        return start <= cur < end
    return cur >= start or cur < end  # overnight window
