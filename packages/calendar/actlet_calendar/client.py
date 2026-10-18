"""Blocking CalDAV wrapper. Call from asyncio.to_thread."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

log = logging.getLogger("actlet.calendar")


@dataclass
class CalendarEvent:
    uid: str
    summary: str
    start: str
    end: str
    description: str = ""
    location: str = ""


class CalendarClient:
    def __init__(self, url: str, username: str, password: str) -> None:
        if not url or not username or not password:
            raise ValueError("CALDAV_URL, CALDAV_USERNAME and CALDAV_PASSWORD are required")
        self._url = url
        self._username = username
        self._password = password

    def _calendar(self):
        import caldav

        client = caldav.DAVClient(
            url=self._url, username=self._username, password=self._password
        )
        principal = client.principal()
        calendars = principal.calendars()
        if not calendars:
            raise RuntimeError("no calendars found at this CalDAV endpoint")
        return calendars[0]

    def verify(self) -> bool:
        self._calendar()
        return True

    def list_events(self, days: int = 7) -> list[CalendarEvent]:
        cal = self._calendar()
        start = datetime.now(UTC)
        end = start + timedelta(days=days)
        events = cal.search(start=start, end=end, event=True, expand=True)
        out: list[CalendarEvent] = []
        for ev in events or []:
            try:
                data = ev.icalendar_component
                out.append(
                    CalendarEvent(
                        uid=str(data.get("uid", "")),
                        summary=str(data.get("summary", "(no title)")),
                        start=str(data.get("dtstart").dt if data.get("dtstart") else ""),
                        end=str(data.get("dtend").dt if data.get("dtend") else ""),
                        description=str(data.get("description", "") or "")[:500],
                        location=str(data.get("location", "") or ""),
                    )
                )
            except Exception:  # noqa: BLE001, S112 — skip malformed events, don't fail the list
                continue
        return sorted(out, key=lambda e: e.start)

    def create_event(
        self,
        summary: str,
        start_iso: str,
        end_iso: str,
        description: str = "",
        location: str = "",
    ) -> str:
        cal = self._calendar()
        start = datetime.fromisoformat(start_iso)
        end = datetime.fromisoformat(end_iso)
        if start.tzinfo is None:
            start = start.replace(tzinfo=UTC)
        if end.tzinfo is None:
            end = end.replace(tzinfo=UTC)
        event_ical = (
            "BEGIN:VCALENDAR\r\nVERSION:2.0\r\nPRODID:-//Actlet//EN\r\n"
            "BEGIN:VEVENT\r\n"
            f"SUMMARY:{summary}\r\n"
            f"DTSTART:{start.strftime('%Y%m%dT%H%M%SZ')}\r\n"
            f"DTEND:{end.strftime('%Y%m%dT%H%M%SZ')}\r\n"
            + (f"DESCRIPTION:{description}\r\n" if description else "")
            + (f"LOCATION:{location}\r\n" if location else "")
            + "END:VEVENT\r\nEND:VCALENDAR\r\n"
        )
        cal.save_event(event_ical)
        log.info("created calendar event %r", summary)
        return summary
