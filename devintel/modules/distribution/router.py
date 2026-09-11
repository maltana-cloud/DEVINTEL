"""Safe destination routing without platform-specific dependencies."""

from dataclasses import dataclass
from typing import Callable, Mapping

from .contracts import DistributionDestination, DistributionMessage, DistributionResult


Sender = Callable[[DistributionMessage], DistributionResult]


@dataclass(frozen=True)
class Route:
    destination: DistributionDestination
    reason: str


class DistributionRouter:
    """Routes approved messages to explicitly registered destinations.

    Missing adapters fail closed. One adapter's exception cannot affect another
    destination. The router does not discover, join, or grant permissions.
    """

    def __init__(self) -> None:
        self._senders: dict[str, Sender] = {}

    def register(self, destination_id: str, sender: Sender) -> None:
        if not destination_id.strip():
            raise ValueError("destination_id must not be empty")
        self._senders[destination_id] = sender

    def unregister(self, destination_id: str) -> None:
        self._senders.pop(destination_id, None)

    def route(self, message: DistributionMessage) -> DistributionResult:
        sender = self._senders.get(message.destination_id)
        if sender is None:
            return DistributionResult(False, message.destination_id, reason="no registered platform adapter")
        try:
            result = sender(message)
            if result.destination_id != message.destination_id:
                return DistributionResult(False, message.destination_id, reason="adapter returned wrong destination")
            return result
        except Exception as exc:
            return DistributionResult(False, message.destination_id, reason=f"adapter failure: {type(exc).__name__}")

    def destinations(self) -> Mapping[str, Sender]:
        return dict(self._senders)
