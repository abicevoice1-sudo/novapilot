"""Slack channel via Socket Mode (no public URL needed).

Setup: create a Slack app at api.slack.com, enable Socket Mode, add the
`app_mentions:read`, `im:read`, `im:write`, `chat:write` scopes, install to
your workspace. Set SLACK_BOT_TOKEN (xoxb-...) and SLACK_APP_TOKEN (xapp-...).
The agent responds to DMs and @-mentions.
"""

from __future__ import annotations

import asyncio
import json
import logging
from collections.abc import Awaitable, Callable

import httpx

from .base import InboundMessage, OutboundMessage

log = logging.getLogger("actlet.channels.slack")


class SlackChannel:
    name = "slack"

    def __init__(
        self,
        bot_token: str,
        app_token: str,
        allowed_users: set[str] | None = None,
    ) -> None:
        if not bot_token or not app_token:
            raise ValueError("SLACK_BOT_TOKEN and SLACK_APP_TOKEN are required")
        self._bot_token = bot_token
        self._app_token = app_token
        self._allowed = allowed_users or set()
        self._task: asyncio.Task | None = None
        self._api: httpx.AsyncClient | None = None

    def _client(self) -> httpx.AsyncClient:
        if self._api is None:
            self._api = httpx.AsyncClient(
                base_url="https://slack.com/api",
                headers={"Authorization": f"Bearer {self._bot_token}"},
                timeout=30.0,
            )
        return self._api

    async def _api_call(self, method: str, **params):
        r = await self._client().post(f"/{method}", json=params)
        r.raise_for_status()
        data = r.json()
        if not data.get("ok"):
            raise RuntimeError(f"slack API error: {data.get('error')}")
        return data

    async def start(self, on_message: Callable[[InboundMessage], Awaitable[None]]) -> None:
        # Verify the bot token, then open a Socket Mode websocket.
        me = await self._api_call("auth.test")
        log.info("slack connected as %s", me.get("user"))
        # Get the websocket URL via apps.connections.open.
        async with httpx.AsyncClient(timeout=30.0) as client:
            r = await client.post(
                "https://slack.com/api/apps.connections.open",
                headers={"Authorization": f"Bearer {self._app_token}"},
            )
            r.raise_for_status()
            ws_url = r.json()["url"]
        self._task = asyncio.create_task(self._socket_loop(ws_url, on_message), name="slack-socket")

    async def stop(self) -> None:
        task, self._task = self._task, None
        if task is not None:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
        if self._api is not None:
            await self._api.aclose()
            self._api = None

    async def send(self, msg: OutboundMessage) -> None:
        text = msg.text or "(empty reply)"
        for i in range(0, len(text), 3500):
            await self._api_call(
                "chat.postMessage", channel=msg.chat_id, text=text[i : i + 3500]
            )

    async def _socket_loop(self, ws_url: str, on_message) -> None:
        import websockets

        while True:
            try:
                async with websockets.connect(ws_url) as ws:
                    async for raw in ws:
                        await self._handle_frame(ws, raw, on_message)
            except asyncio.CancelledError:
                raise
            except Exception:
                log.exception("slack socket failed, reconnecting in 5s")
                await asyncio.sleep(5)

    async def _handle_frame(self, ws, raw: str, on_message) -> None:
        try:
            frame = json.loads(raw)
        except json.JSONDecodeError:
            return
        # Acknowledge every envelope.
        if "envelope_id" in frame:
            await ws.send(json.dumps({"envelope_id": frame["envelope_id"]}))
        if frame.get("type") != "events_api":
            return
        event = (frame.get("payload") or {}).get("event") or {}
        if event.get("type") != "message" or event.get("bot_id"):
            return
        user = event.get("user", "")
        if self._allowed and user not in self._allowed:
            log.info("ignoring slack message from non-allowed user %s", user)
            return
        text = event.get("text", "")
        # Only respond to DMs or @-mentions (avoid channel noise).
        channel_type = event.get("channel_type", "")
        if channel_type != "im" and "<@" not in text:
            return
        await on_message(
            InboundMessage(
                channel="slack",
                chat_id=event.get("channel", ""),
                sender_id=user,
                sender_name=user,
                text=text,
                message_id=event.get("ts", ""),
            )
        )
