"""Blocking IMAP/SMTP client (stdlib only). Call from asyncio.to_thread."""

from __future__ import annotations

import email
import email.policy
import imaplib
import logging
import smtplib
from dataclasses import dataclass
from email.message import EmailMessage

log = logging.getLogger("novapilot.gmail")


@dataclass
class GmailMessage:
    uid: str
    from_addr: str
    to_addr: str
    subject: str
    date: str
    snippet: str
    body: str = ""
    unread: bool = False


def _text_body(msg: EmailMessage) -> str:
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == "text/plain" and not part.get_filename():
                try:
                    return part.get_content()
                except Exception:  # noqa: BLE001, S112
                    continue
        return ""
    try:
        return msg.get_content()
    except Exception:  # noqa: BLE001
        return ""


class GmailClient:
    def __init__(
        self,
        address: str,
        app_password: str,
        imap_host: str = "imap.gmail.com",
        smtp_host: str = "smtp.gmail.com",
    ) -> None:
        if not address or not app_password:
            raise ValueError("GMAIL_ADDRESS and GMAIL_APP_PASSWORD are required")
        self._address = address
        self._password = app_password
        self._imap_host = imap_host
        self._smtp_host = smtp_host

    def _imap(self) -> imaplib.IMAP4_SSL:
        conn = imaplib.IMAP4_SSL(self._imap_host)
        conn.login(self._address, self._password)
        return conn

    def verify(self) -> bool:
        """Log in and back out. Raises on bad credentials."""
        conn = self._imap()
        try:
            conn.logout()
        except Exception:  # noqa: BLE001, S110
            pass
        return True

    def list_messages(
        self, folder: str = "INBOX", limit: int = 10, unread_only: bool = False
    ) -> list[GmailMessage]:
        conn = self._imap()
        try:
            conn.select(folder, readonly=True)
            criterion = "UNSEEN" if unread_only else "ALL"
            _, data = conn.search(None, criterion)
            uids = data[0].split()
            result: list[GmailMessage] = []
            for uid in uids[-limit:]:
                _, fetched = conn.fetch(uid, "(BODY.PEEK[HEADER.FIELDS (FROM TO SUBJECT DATE)] FLAGS)")
                raw = fetched[0][1] if fetched and fetched[0] else b""
                msg = email.message_from_bytes(raw, policy=email.policy.default)
                flags = fetched[0][0] if fetched and fetched[0] else b""
                result.append(
                    GmailMessage(
                        uid=uid.decode(),
                        from_addr=str(msg.get("From", "")),
                        to_addr=str(msg.get("To", "")),
                        subject=str(msg.get("Subject", "")),
                        date=str(msg.get("Date", "")),
                        snippet="",
                        unread=b"\\Seen" not in flags,
                    )
                )
            return result
        finally:
            try:
                conn.logout()
            except Exception:  # noqa: BLE001, S110
                pass

    def read_message(self, uid: str, folder: str = "INBOX", mark_seen: bool = False) -> GmailMessage:
        conn = self._imap()
        try:
            conn.select(folder, readonly=not mark_seen)
            peek = "" if mark_seen else ".PEEK"
            _, fetched = conn.fetch(uid.encode(), f"(BODY{peek}[] FLAGS)")
            raw = fetched[0][1] if fetched and fetched[0] else b""
            msg = email.message_from_bytes(raw, policy=email.policy.default)
            body = _text_body(msg)
            flags = fetched[0][0] if fetched and fetched[0] else b""
            return GmailMessage(
                uid=uid,
                from_addr=str(msg.get("From", "")),
                to_addr=str(msg.get("To", "")),
                subject=str(msg.get("Subject", "")),
                date=str(msg.get("Date", "")),
                snippet=body[:200].replace("\n", " "),
                body=body[:20000],
                unread=b"\\Seen" not in flags,
            )
        finally:
            try:
                conn.logout()
            except Exception:  # noqa: BLE001, S110
                pass

    def mark_seen(self, uid: str, folder: str = "INBOX") -> None:
        conn = self._imap()
        try:
            conn.select(folder)
            conn.store(uid.encode(), "+FLAGS", "\\Seen")
        finally:
            try:
                conn.logout()
            except Exception:  # noqa: BLE001, S110
                pass

    def send(self, to: str, subject: str, body: str) -> None:
        msg = EmailMessage()
        msg["From"] = self._address
        msg["To"] = to
        msg["Subject"] = subject
        msg.set_content(body)
        with smtplib.SMTP_SSL(self._smtp_host, 465) as smtp:
            smtp.login(self._address, self._password)
            smtp.send_message(msg)
        log.info("sent email to %s (%d chars)", to, len(body))
