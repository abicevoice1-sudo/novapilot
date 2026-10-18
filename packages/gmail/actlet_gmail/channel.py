"""Gmail inbound channel: poll UNSEEN, hand each to the agent, mark seen.

Each new email becomes a fully-supervised task (source=gmail:<uid>), exactly
like the Telegram channel. Replies go back via gmail_send (approval-gated),
not automatically — the agent decides.
"""

from __future__ import annotations

import asyncio
import logging
from collections.abc import Awaitable, Callable
from typing import TYPE_CHECKING

from .client import GmailClient

if TYPE_CHECKING:
    from actlet_channels.base import InboundMessage, OutboundMessage

log = logging.getLogger("actlet.channels.gmail")


class GmailChannel:
    name = "gmail"

    def __init__(
        self,
        client_factory: Callable[[], GmailClient],
        poll_interval: float = 60.0,
        allowed_senders: set[str] | None = None,
    ) -> None:
        self._factory = client_factory
        self._poll_interval = poll_interval
        self._allowed = {s.lower() for s in (allowed_senders or set())}
        self._task: asyncio.Task | None = None

    async def start(
        self, on_message: Callable[[InboundMessage], Awaitable[None]]
    ) -> None:
        from actlet_channels.base import InboundMessage

        client = self._factory()
        await asyncio.to_thread(client.verify)
        log.info("gmail channel connected, polling every %ss", self._poll_interval)
        self._task = asyncio.create_task(
            self._poll(on_message, InboundMessage), name="gmail-poll"
        )

    async def stop(self) -> None:
        task, self._task = self._task, None
        if task is not None:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass

    async def send(self, msg: OutboundMessage) -> None:
        # Replies go through the approval-gated gmail_send tool, not here.
        raise NotImplementedError(
            "gmail channel does not send directly; the agent uses gmail_send"
        )

    async def _poll(self, on_message, InboundMessage) -> None:
        while True:
            try:
                await self._check(on_message, InboundMessage)
            except asyncio.CancelledError:
                raise
            except Exception:
                log.exception("gmail poll failed")
            await asyncio.sleep(self._poll_interval)

    async def _check(self, on_message, InboundMessage) -> None:
        client = self._factory()
        unseen = await asyncio.to_thread(client.list_messages, "INBOX", 20, True)
        for m in unseen:
            sender = m.from_addr.lower()
            # Deny-by-default: empty allowlist = no sender accepted (audit fix).
            if not any(a in sender for a in self._allowed):
                log.info("ignoring email from non-allowed sender %s", m.from_addr)
                await asyncio.to_thread(client.mark_seen, m.uid)
                continue
            full = await asyncio.to_thread(client.read_message, m.uid)
            text = (
                f"Email from {full.from_addr}\nSubject: {full.subject}\n"
                f"Date: {full.date}\n\n{full.body[:4000]}"
            )
            await on_message(
                InboundMessage(
                    channel="gmail",
                    chat_id=full.from_addr,
                    sender_id=full.from_addr,
                    sender_name=full.from_addr,
                    text=text,
                    message_id=m.uid,
                )
            )
            await asyncio.to_thread(client.mark_seen, m.uid)
