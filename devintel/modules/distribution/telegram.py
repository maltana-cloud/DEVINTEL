"""Telegram adapter boundary.

No network client is required by the core. A concrete transport is injected,
keeping credentials and platform details outside DEVINTEL's intelligence layer.
"""

from dataclasses import dataclass
from typing import Callable, Mapping

from .contracts import DistributionDestination, DistributionMessage, DistributionResult


@dataclass(frozen=True)
class TelegramUpdate:
    update_id: str
    destination_id: str
    sender_id: str
    text: str
    message_id: str = ""
    metadata: Mapping[str, str] = None


SendTransport = Callable[[str, str], str]


class TelegramAdapter:
    """Thin, injectable Telegram transport; never discovers authority itself."""

    platform = "telegram"

    def __init__(self, send_transport: SendTransport | None = None) -> None:
        self._send_transport = send_transport

    def send(self, destination: DistributionDestination, message: DistributionMessage) -> DistributionResult:
        if destination.platform.lower() != self.platform:
            return DistributionResult(False, message.destination_id, reason="destination is not Telegram")
        if self._send_transport is None:
            return DistributionResult(False, message.destination_id, reason="Telegram transport is not configured")
        try:
            message_id = self._send_transport(destination.destination_id, message.text)
            if not isinstance(message_id, str) or not message_id:
                return DistributionResult(False, message.destination_id, reason="invalid Telegram transport result")
            return DistributionResult(True, message.destination_id, message_id)
        except Exception as exc:
            return DistributionResult(False, message.destination_id, reason=f"Telegram transport failure: {type(exc).__name__}")

    def parse_update(self, update: Mapping[str, object]) -> TelegramUpdate:
        """Convert untrusted Telegram-like input into a bounded local contract."""
        if not isinstance(update, Mapping):
            raise ValueError("update must be a mapping")
        values = {key: update.get(key, "") for key in ("update_id", "destination_id", "sender_id", "text", "message_id")}
        if any(not isinstance(value, str) or not value.strip() for value in values.values() if value is not values["message_id"]):
            raise ValueError("required update fields must be non-empty strings")
        return TelegramUpdate(**values, metadata={})
