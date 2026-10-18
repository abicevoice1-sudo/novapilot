"""Slack channel tests: frame handling, filters, chunking. No real Slack."""

import json
from unittest.mock import AsyncMock

import pytest
import respx

from actlet_channels.base import InboundMessage
from actlet_channels.slack import SlackChannel


@pytest.fixture(autouse=True)
def no_proxy_env(monkeypatch):
    """respx + ambient proxy env vars don't mix; tests must be hermetic."""
    for var in ("HTTP_PROXY", "HTTPS_PROXY", "http_proxy", "https_proxy",
                "ALL_PROXY", "all_proxy", "NO_PROXY", "no_proxy"):
        monkeypatch.delenv(var, raising=False)


def _frame(event):
    return json.dumps({
        "envelope_id": "env-1",
        "type": "events_api",
        "payload": {"event": event},
    })


def _msg_event(text="hello", channel_type="im", user="U123", ts="1.0"):
    return {
        "type": "message",
        "user": user,
        "text": text,
        "channel": "D123",
        "channel_type": channel_type,
        "ts": ts,
    }


@pytest.fixture()
def channel():
    with respx.mock:
        yield SlackChannel("xoxb-test", "xapp-test", allowed_users={"U123"})


async def test_dm_reaches_agent(channel):
    received = []

    async def on_message(m: InboundMessage):
        received.append(m)

    ws = AsyncMock()
    await channel._handle_frame(ws, _frame(_msg_event("do the thing")), on_message)
    # envelope acknowledged
    ws.send.assert_called_once()
    assert len(received) == 1
    assert received[0].channel == "slack"
    assert received[0].text == "do the thing"
    assert received[0].sender_id == "U123"


async def test_channel_message_without_mention_ignored(channel):
    received = []

    async def on_message(m):
        received.append(m)

    ws = AsyncMock()
    await channel._handle_frame(
        ws, _frame(_msg_event("random chat", channel_type="channel")), on_message
    )
    assert received == []


async def test_channel_mention_reaches_agent(channel):
    received = []

    async def on_message(m):
        received.append(m)

    ws = AsyncMock()
    await channel._handle_frame(
        ws, _frame(_msg_event("<@U999> help me", channel_type="channel")), on_message
    )
    assert len(received) == 1


async def test_bot_messages_ignored(channel):
    received = []

    async def on_message(m):
        received.append(m)

    ws = AsyncMock()
    event = _msg_event("bot says hi")
    event["bot_id"] = "B123"
    await channel._handle_frame(ws, _frame(event), on_message)
    assert received == []


async def test_non_allowed_user_ignored():
    ch = SlackChannel("xoxb-test", "xapp-test", allowed_users={"U999"})
    received = []

    async def on_message(m):
        received.append(m)

    ws = AsyncMock()
    await ch._handle_frame(ws, _frame(_msg_event("hi", user="U123")), on_message)
    assert received == []


async def test_requires_tokens():
    with pytest.raises(ValueError, match="SLACK_BOT_TOKEN"):
        SlackChannel("", "")


@respx.mock
async def test_send_chunks_long_messages():
    import httpx as _httpx

    ch = SlackChannel("xoxb-test", "xapp-test", allowed_users={"U123"})
    route = respx.post("https://slack.com/api/chat.postMessage").mock(
        return_value=_httpx.Response(200, json={"ok": True})
    )
    from actlet_channels.base import OutboundMessage

    await ch.send(OutboundMessage(chat_id="D123", text="x" * 4000))
    assert route.call_count == 2
    await ch.stop()
