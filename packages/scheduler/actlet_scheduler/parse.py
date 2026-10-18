"""Natural-language schedule parsing.

Understands the patterns people actually type. Anything else raises
ScheduleParseError with an honest message — never a guessed cron.
"""

from __future__ import annotations

import re

WEEKDAYS = {
    "monday": "mon", "tuesday": "tue", "wednesday": "wed", "thursday": "thu",
    "friday": "fri", "saturday": "sat", "sunday": "sun",
    "mon": "mon", "tue": "tue", "wed": "wed", "thu": "thu",
    "fri": "fri", "sat": "sat", "sun": "sun",
}


class ScheduleParseError(ValueError):
    pass


def _parse_time(text: str) -> tuple[int, int]:
    """'8:30am', '8:30 am', '0830', '8am', '20:15' -> (hour, minute)."""
    m = re.fullmatch(r"\s*(\d{1,2})(?::(\d{2}))?\s*(am|pm)?\s*", text, re.IGNORECASE)
    if not m:
        raise ScheduleParseError(f"could not parse time {text!r}")
    hour, minute, meridiem = int(m.group(1)), int(m.group(2) or 0), (m.group(3) or "").lower()
    if meridiem == "pm" and hour < 12:
        hour += 12
    if meridiem == "am" and hour == 12:
        hour = 0
    if not (0 <= hour <= 23 and 0 <= minute <= 59):
        raise ScheduleParseError(f"invalid time {text!r}")
    return hour, minute


def parse_schedule(text: str) -> dict:
    """Parse 'every morning at 8' etc. Returns {'cron': ...} or {'interval_sec': ...}.

    Raises ScheduleParseError when the text is not understood.
    """
    t = text.strip().lower()
    if not t:
        raise ScheduleParseError("empty schedule")

    # every N seconds/minutes/hours
    m = re.fullmatch(r"every (\d+)\s*(second|minute|hour)s?", t)
    if m:
        n, unit = int(m.group(1)), m.group(2)
        if n <= 0:
            raise ScheduleParseError("interval must be positive")
        mult = {"second": 1, "minute": 60, "hour": 3600}[unit]
        return {"interval_sec": n * mult}

    if t == "hourly":
        return {"interval_sec": 3600}

    # every <weekday>(, <weekday>)* [at <time>]
    m = re.fullmatch(
        r"every ((?:mon|tue|wed|thu|fri|sat|sun|monday|tuesday|wednesday|thursday|friday|saturday|sunday)"
        r"(?:\s*(?:,|and)\s*(?:mon|tue|wed|thu|fri|sat|sun|monday|tuesday|wednesday|thursday|friday|saturday|sunday))*)"
        r"(?:\s+at\s+(.+))?",
        t,
    )
    if m:
        days = ",".join(
            sorted({WEEKDAYS[d] for d in re.split(r"\s*(?:,|and)\s*", m.group(1))})
        )
        hour, minute = _parse_time(m.group(2)) if m.group(2) else (9, 0)
        return {"cron": f"{minute} {hour} * * {days}"}

    # every day|morning|evening|night [at <time>]  /  daily [at <time>]
    m = re.fullmatch(r"(?:every\s+)?(day|daily|morning|evening|night)(?:\s+at\s+(.+))?", t)
    if m:
        word, when = m.group(1), m.group(2)
        if when:
            hour, minute = _parse_time(when)
        else:
            hour, minute = {"morning": (8, 0), "evening": (18, 0), "night": (21, 0)}.get(
                word, (9, 0)
            )
        return {"cron": f"{minute} {hour} * * *"}

    raise ScheduleParseError(
        f"did not understand {text!r}. Try 'every morning at 8', "
        "'every monday at 9am', 'every 30 minutes', or a cron string."
    )
