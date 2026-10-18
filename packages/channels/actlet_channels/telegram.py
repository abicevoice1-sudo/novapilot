"""Telegram channel: long-poll Bot API, no webhook server needed.

Setup: message @BotFather on Telegram, create a bot, set TELEGRAM_BOT_TOKEN.
Optionally set TELEGRAM_ALLOWED_USERS="12345,67890" to restrict who can talk
to your agent (default: anyone who finds the bot — set this).
"""

from __future__ import annotations

import asyncio
import logging
from collections.abc import Awaitable, Callable

import httpx

from .base import InboundMessage, OutboundMessage

log = logging.getLogger("actlet.channels.telegram")


class TelegramChannel:
    name = "telegram"

    def __init__(
        self,
        bot_token: str,
        allowed_users: set[str] | None = None,
        poll_interval: float = 1.0,
    ) -> None:
        if not bot_token:
            raise ValueError("TELEGRAM_BOT_TOKEN is required")
        self._token = bot_token
        self._allowed = allowed_users or set()
        self._poll_interval = poll_interval
        self._client: httpx.AsyncClient | None = None
        self._task: asyncio.Task | None = None
        self._offset = 0

    def _url(self, method: str) -> str:
        return f"https://api.telegram.org/bot{self._token}/{method}"

    async def start(self, on_message: Callable[[InboundMessage], Awaitable[None]]) -> None:
        self._client = httpx.AsyncClient(timeout=35.0)
        # Verify the token before polling.
        r = await self._client.get(self._url("getMe"))
        r.raise_for_status()
        me = r.json()["result"]
        log.info("telegram connected as @%s", me.get("username"))
        self._task = asyncio.create_task(self._poll(on_message), name="telegram-poll")

    async def stop(self) -> None:
        task, self._task = self._task, None
        if task is not None:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
        if self._client is not None:
            await self._client.aclose()
            self._client = None

    async def send(self, msg: OutboundMessage) -> None:
        assert self._client is not None, "channel not started"
        # Telegram caps messages at 4096 chars; chunk long replies.
        text = msg.text or "(empty reply)"
        for i in range(0, len(text), 4000):
            r = await self._client.post(
                self._url("sendMessage"),
                json={"chat_id": msg.chat_id, "text": text[i : i + 4000]},
            )
            r.raise_for_status()

    async def _poll(self, on_message: Callable[[InboundMessage], Awaitable[None]]) -> None:
        assert self._client is not None
        while True:
            try:
                r = await self._client.get(
                    self._url("getUpdates"),
                    params={"offset": self._offset, "timeout": 30, "allowed_updates": ["message"]},
                )
                r.raise_for_status()
                for update in r.json().get("result", []):
                    self._offset = update["update_id"] + 1
                    msg = update.get("message") or {}
                    text = (msg.get("text") or "").strip()
                    if not text:
                        continue
                    sender = msg.get("from") or {}
                    sender_id = str(sender.get("id", ""))
                    # Deny-by-default: empty allowlist = no one may use the bot (audit fix).
                    if sender_id not in self._allowed:
                        log.warning("telegram: ignoring message from unauthorized user %s", sender_id)
                        continue
                    await on_message(
                        InboundMessage(
                            channel="telegram",
                            chat_id=str(msg["chat"]["id"]),
                            sender_id=sender_id,
                            sender_name=sender.get("first_name", "user"),
                            text=text,
                            message_id=str(msg.get("message_id", "")),
                        )
                    )
            except asyncio.CancelledError:
                raise
            except Exception:
                log.exception("telegram poll error; retrying")
                await asyncio.sleep(self._poll_interval)
