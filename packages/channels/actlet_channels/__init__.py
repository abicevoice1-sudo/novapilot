"""Actlet channels: reach the agent from messaging apps."""

from .base import ChannelPlugin, InboundMessage, OutboundMessage
from .slack import SlackChannel
from .telegram import TelegramChannel

__all__ = ["ChannelPlugin", "InboundMessage", "OutboundMessage", "SlackChannel", "TelegramChannel"]
