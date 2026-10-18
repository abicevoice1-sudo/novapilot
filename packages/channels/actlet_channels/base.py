"""Channel plugin contract."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import Protocol


@dataclass
class InboundMessage:
    channel: str          # "telegram"
    chat_id: str          # where to reply
    sender_id: str
    sender_name: str
    text: str
    message_id: str = ""


@dataclass
class OutboundMessage:
    chat_id: str
    text: str
    reply_to: str = ""


class ChannelPlugin(Protocol):
    name: str

    async def start(self, on_message: Callable[[InboundMessage], Awaitable[None]]) -> None: ...
    async def stop(self) -> None: ...
    async def send(self, msg: OutboundMessage) -> None: ...
