"""Calendar integration: CalDAV client + agent tools.

Setup: Google Calendar works over CalDAV with an App Password
(same as Gmail): set CALDAV_URL (https://apidata.googleusercontent.com/caldav/v2/you@gmail.com/events),
CALDAV_USERNAME, CALDAV_PASSWORD. Also works with Nextcloud, Fastmail, iCloud, etc.
"""

from .client import CalendarClient, CalendarEvent
from .tools import register_calendar_tools

__all__ = ["CalendarClient", "CalendarEvent", "register_calendar_tools"]
