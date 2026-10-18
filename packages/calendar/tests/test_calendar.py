"""Calendar tests: client parsing + tools, with mocked caldav."""

from __future__ import annotations

from datetime import UTC, datetime
from unittest.mock import MagicMock, patch

import pytest
from actlet_agent.tools import ToolRegistry

from actlet_calendar import CalendarClient, register_calendar_tools


def _fake_event(summary="Team standup"):
    comp = {
        "uid": "evt-1",
        "summary": summary,
        "dtstart": MagicMock(dt=datetime(2026, 10, 19, 14, 0, tzinfo=UTC)),
        "dtend": MagicMock(dt=datetime(2026, 10, 19, 14, 30, tzinfo=UTC)),
        "description": "daily sync",
        "location": "Zoom",
    }
    ev = MagicMock()
    ev.icalendar_component = comp
    # dict-like .get on the component
    comp_get = comp.get
    ev.icalendar_component = MagicMock()
    ev.icalendar_component.get = comp_get
    return ev


def _client():
    with patch("caldav.DAVClient") as dav_cls:
        client = dav_cls.return_value
        principal = client.principal.return_value
        calendar = MagicMock()
        principal.calendars.return_value = [calendar]
        calendar.search.return_value = [_fake_event()]
        yield CalendarClient("https://caldav.example/events", "user", "pw"), calendar


def test_list_events():
    with patch("caldav.DAVClient") as dav_cls:
        client = dav_cls.return_value
        principal = client.principal.return_value
        calendar = MagicMock()
        principal.calendars.return_value = [calendar]
        calendar.search.return_value = [_fake_event("Standup"), _fake_event("Lunch")]

        gmail = CalendarClient("https://caldav.example/events", "user", "pw")
        events = gmail.list_events(days=7)
        assert len(events) == 2
        assert events[0].summary == "Standup"
        assert "2026-10-19" in events[0].start


def test_create_event_builds_ical():
    with patch("caldav.DAVClient") as dav_cls:
        client = dav_cls.return_value
        principal = client.principal.return_value
        calendar = MagicMock()
        principal.calendars.return_value = [calendar]

        c = CalendarClient("https://caldav.example/events", "user", "pw")
        c.create_event("Dentist", "2026-10-20T10:00:00", "2026-10-20T11:00:00")
        ical = calendar.save_event.call_args[0][0]
        assert "SUMMARY:Dentist" in ical
        assert "DTSTART:20261020T100000Z" in ical


def test_requires_credentials():
    with pytest.raises(ValueError, match="CALDAV_URL"):
        CalendarClient("", "", "")


def test_no_calendars_raises():
    with patch("caldav.DAVClient") as dav_cls:
        dav_cls.return_value.principal.return_value.calendars.return_value = []
        with pytest.raises(RuntimeError, match="no calendars"):
            CalendarClient("https://x", "u", "p").list_events()


async def test_tools_registered():
    with patch("caldav.DAVClient") as dav_cls:
        client = dav_cls.return_value
        principal = client.principal.return_value
        calendar = MagicMock()
        principal.calendars.return_value = [calendar]
        calendar.search.return_value = [_fake_event()]

        reg = ToolRegistry()
        register_calendar_tools(
            reg, lambda: CalendarClient("https://x", "u", "p")
        )
        names = {t["name"] for t in reg.specs()}
        assert {"calendar_list", "calendar_create"} <= names
        create_spec = next(t for t in reg.specs() if t["name"] == "calendar_create")
        assert create_spec["risk"] == "high"
        assert create_spec["requires_approval"] is True

        result, _ = await reg.call("calendar_list", {"days": 7})
        assert result.ok and "Team standup" in result.output
