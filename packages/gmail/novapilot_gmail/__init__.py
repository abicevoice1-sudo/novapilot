"""Gmail integration: IMAP/SMTP client, agent tools, inbound channel.

Setup: create a Google App Password (Google Account → Security → 2-Step
Verification → App passwords), then set GMAIL_ADDRESS and GMAIL_APP_PASSWORD.
The password is only ever read from the environment, never logged.
"""

from .channel import GmailChannel
from .client import GmailClient, GmailMessage
from .tools import register_gmail_tools

__all__ = ["GmailChannel", "GmailClient", "GmailMessage", "register_gmail_tools"]
