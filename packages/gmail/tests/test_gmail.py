"""Gmail tests: client parsing + tools + channel, all with mocked IMAP/SMTP."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
from novapilot_agent.tools import ToolRegistry

from novapilot_gmail import GmailChannel, GmailClient, register_gmail_tools

RAW = (
    b"From: Alice <alice@example.com>\r\n"
    b"To: me@gmail.com\r\n"
    b"Subject: Hello\r\n"
    b"Date: Sun, 18 Oct 2026 10:00:00 +0000\r\n"
    b"\r\n"
    b"Hi there, this is the body.\r\n"
)


def _fake_imap(uids=(b"1", b"2"), unseen: tuple = (b"2",)):
    conn = MagicMock()
    conn.search.return_value = ("OK", [b" ".join(uids)])
    def fetch(uid, _spec):
        flags = b"" if uid in unseen else b"\\Seen"
        return ("OK", [(flags, RAW)])
    conn.fetch.side_effect = fetch
    return conn


@pytest.fixture()
def client():
    with patch("imaplib.IMAP4_SSL") as imap_cls:
        conn = _fake_imap()
        imap_cls.return_value = conn
        yield GmailClient("me@gmail.com", "app-password"), conn


def test_list_messages(client):
    gmail, _conn = client
    msgs = gmail.list_messages(limit=10)
    assert len(msgs) == 2
    assert msgs[1].unread is True
    assert msgs[0].unread is False
    assert msgs[1].subject == "Hello"
    assert "alice@example.com" in msgs[1].from_addr


def test_read_message_body(client):
    gmail, _conn = client
    m = gmail.read_message("2")
    assert "Hi there" in m.body
    assert m.snippet.startswith("Hi there")


def test_send_uses_smtp_ssl():
    with patch("smtplib.SMTP_SSL") as smtp_cls:
        smtp = MagicMock()
        smtp_cls.return_value.__enter__.return_value = smtp
        GmailClient("me@gmail.com", "pw").send("bob@x.com", "Sub", "Body")
        smtp.login.assert_called_once_with("me@gmail.com", "pw")
        sent = smtp.send_message.call_args[0][0]
        assert sent["To"] == "bob@x.com"
        assert sent["Subject"] == "Sub"


def test_requires_credentials():
    with pytest.raises(ValueError, match="GMAIL_ADDRESS"):
        GmailClient("", "")


async def test_tools_registered():
    with patch("imaplib.IMAP4_SSL") as imap_cls:
        imap_cls.return_value = _fake_imap()
        reg = ToolRegistry()
        register_gmail_tools(reg, lambda: GmailClient("me@gmail.com", "pw"))
        names = {t["name"] for t in reg.specs()}
        assert {"gmail_list", "gmail_read", "gmail_send"} <= names
        send_spec = next(t for t in reg.specs() if t["name"] == "gmail_send")
        assert send_spec["risk"] == "high"
        assert send_spec["requires_approval"] is True

        result, _ = await reg.call("gmail_list", {"limit": 5})
        assert result.ok and "Hello" in result.output


async def test_channel_hands_unseen_to_agent():
    from novapilot_channels.base import InboundMessage

    with patch("imaplib.IMAP4_SSL") as imap_cls:
        conn = _fake_imap(uids=(b"7",), unseen=(b"7",))
        imap_cls.return_value = conn
        received: list[InboundMessage] = []

        async def on_message(m: InboundMessage):
            received.append(m)

        ch = GmailChannel(lambda: GmailClient("me@gmail.com", "pw"))
        await ch._check(on_message, InboundMessage)
        assert len(received) == 1
        assert received[0].channel == "gmail"
        assert "Hello" in received[0].text
        # marked seen after handling
        conn.store.assert_called()


async def test_channel_ignores_non_allowed_senders():
    from novapilot_channels.base import InboundMessage

    with patch("imaplib.IMAP4_SSL") as imap_cls:
        conn = _fake_imap(uids=(b"7",), unseen=(b"7",))
        imap_cls.return_value = conn
        received = []

        async def on_message(m):
            received.append(m)

        ch = GmailChannel(
            lambda: GmailClient("me@gmail.com", "pw"),
            allowed_senders={"boss@company.com"},
        )
        await ch._check(on_message, InboundMessage)
        assert received == []
        conn.store.assert_called()  # still marked seen so it isn't retried
