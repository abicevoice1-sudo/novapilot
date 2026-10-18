"""Channel manager: messaging apps -> agent tasks -> replies.

Inbound message -> TaskRunner task (fully supervised: no pre-approved tools).
On completion the summary goes back to the chat. If the task hits an
approval gate, the chat is told to approve in the web UI.
"""

from __future__ import annotations

import asyncio
import logging

from actlet_channels import InboundMessage, OutboundMessage, TelegramChannel

from .config import settings

log = logging.getLogger("actlet.channels")

_manager = None


class ChannelManager:
    def __init__(self) -> None:
        self.channels: dict = {}
        self._watchers: set[asyncio.Task] = set()

    def configure(self) -> None:
        token = settings.telegram_bot_token
        if token:
            allowed = {
                u.strip() for u in (settings.telegram_allowed_users or "").split(",") if u.strip()
            }
            self.channels["telegram"] = TelegramChannel(token, allowed_users=allowed)
            log.info("telegram channel configured (allowed_users=%s)",
                     sorted(allowed) or "anyone")
        if settings.gmail_address and settings.gmail_app_password:
            from actlet_gmail import GmailChannel, GmailClient

            def _factory() -> GmailClient:
                return GmailClient(settings.gmail_address, settings.gmail_app_password)

            allowed_senders = {
                s.strip().lower()
                for s in (settings.gmail_allowed_senders or "").split(",")
                if s.strip()
            }
            self.channels["gmail"] = GmailChannel(_factory, allowed_senders=allowed_senders)
            log.info("gmail channel configured (allowed_senders=%s)",
                     sorted(allowed_senders) or "anyone")

    async def start(self) -> None:
        for name, ch in self.channels.items():
            try:
                await ch.start(self._on_message)
                log.info("channel %s started", name)
            except Exception:
                log.exception("channel %s failed to start", name)

    async def stop(self) -> None:
        for task in self._watchers:
            task.cancel()
        self._watchers.clear()
        for name, ch in self.channels.items():
            try:
                await ch.stop()
            except Exception:
                log.exception("channel %s failed to stop", name)

    def status(self) -> dict:
        return {
            name: {"connected": ch._task is not None}
            for name, ch in self.channels.items()
        }

    async def _on_message(self, msg: InboundMessage) -> None:
        from .agent import get_runner
        from .control import is_paused

        log.info("channel %s: message from %s", msg.channel, msg.sender_name)
        if is_paused():
            log.info("channel %s: ignoring message (agent paused)", msg.channel)
            return
        task_id = await get_runner().create_task(
            msg.text, source=f"{msg.channel}:{msg.chat_id}"
        )
        watcher = asyncio.create_task(self._watch(msg, task_id))
        self._watchers.add(watcher)
        watcher.add_done_callback(self._watchers.discard)

    async def _watch(self, msg: InboundMessage, task_id: str) -> None:
        from .agent import get_runner

        runner = get_runner()
        ch = self.channels[msg.channel]
        await ch.send(OutboundMessage(chat_id=msg.chat_id, text="On it — I'll report back."))
        notified_approval = False
        while True:
            await asyncio.sleep(2)
            try:
                state = await runner.get_state(task_id)
            except Exception:  # noqa: BLE001, S112 — transient; keep watching
                continue
            if state is None:
                return
            status = state.get("status")
            if status == "waiting_approval" and not notified_approval:
                pending = state.get("pending_approval") or {}
                step = (pending.get("step") or {}).get("description", "a step")
                await ch.send(OutboundMessage(
                    chat_id=msg.chat_id,
                    text=f"I need your approval in the web UI to continue: {step}",
                ))
                notified_approval = True
            elif status in ("completed", "failed", "cancelled", "paused"):
                summary = state.get("summary") or state.get("error") or "(no summary)"
                if status != "completed":
                    summary = f"Task {status}: {summary}"
                await ch.send(OutboundMessage(chat_id=msg.chat_id, text=summary[:3500]))
                return


def get_channel_manager() -> ChannelManager:
    global _manager
    if _manager is None:
        _manager = ChannelManager()
        _manager.configure()
    return _manager
