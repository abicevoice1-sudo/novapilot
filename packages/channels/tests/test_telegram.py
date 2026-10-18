"""Telegram channel tests (respx-mocked Bot API — no network)."""

import asyncio

import pytest
import respx
from httpx import Response

from novapilot_channels import InboundMessage, OutboundMessage, TelegramChannel

TOKEN = "test-token-123"
BASE = f"https://api.telegram.org/bot{TOKEN}"


@pytest.fixture(autouse=True)
def no_proxy_env(monkeypatch):
    """respx + ambient proxy env vars don't mix; tests must be hermetic."""
    for var in ("HTTP_PROXY", "HTTPS_PROXY", "http_proxy", "https_proxy",
                "ALL_PROXY", "all_proxy", "NO_PROXY", "no_proxy"):
        monkeypatch.delenv(var, raising=False)


def _me():
    return respx.get(f"{BASE}/getMe").mock(
        return_value=Response(200, json={"ok": True, "result": {"username": "novapilot_bot"}})
    )


@respx.mock
async def test_start_verifies_token():
    _me()
    respx.get(f"{BASE}/getUpdates").mock(
        return_value=Response(200, json={"ok": True, "result": []})
    )
    ch = TelegramChannel(TOKEN)
    await ch.start(lambda m: asyncio.sleep(0))
    assert ch._task is not None
    await ch.stop()


def _updates_route(updates):
    """Serve `updates` once, then empty lists."""
    empties = [Response(200, json={"ok": True, "result": []}) for _ in range(20)]
    return respx.get(f"{BASE}/getUpdates").mock(
        side_effect=[Response(200, json={"ok": True, "result": updates}), *empties]
    )


def _update(text, user_id=42, name="Syed"):
    return {
        "update_id": 7,
        "message": {
            "message_id": 1,
            "chat": {"id": 555},
            "from": {"id": user_id, "first_name": name},
            "text": text,
        },
    }


@respx.mock
async def test_inbound_message_dispatched():
    _me()
    _updates_route([_update("hello nova")])
    ch = TelegramChannel(TOKEN)
    received: list[InboundMessage] = []
    await ch.start(received.append)
    for _ in range(100):
        if received:
            break
        await asyncio.sleep(0.05)
    await ch.stop()
    assert len(received) == 1
    assert received[0].text == "hello nova"
    assert received[0].sender_name == "Syed"
    assert received[0].chat_id == "555"


@respx.mock
async def test_unauthorized_user_ignored():
    _me()
    _updates_route([_update("rm -rf /", user_id=999, name="Stranger")])
    ch = TelegramChannel(TOKEN, allowed_users={"42"})
    received = []
    await ch.start(received.append)
    await asyncio.sleep(1.0)
    await ch.stop()
    assert received == []


@respx.mock
async def test_send_chunks_long_messages():
    import httpx

    route = respx.post(f"{BASE}/sendMessage").mock(
        return_value=Response(200, json={"ok": True})
    )
    ch = TelegramChannel(TOKEN)
    ch._client = httpx.AsyncClient()
    try:
        await ch.send(OutboundMessage(chat_id="1", text="x" * 9000))
    finally:
        await ch._client.aclose()
    assert route.call_count == 3  # 4000 + 4000 + 1000


def test_token_required():
    with pytest.raises(ValueError):
        TelegramChannel("")
