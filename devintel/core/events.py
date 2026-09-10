"""Thread-safe in-process event bus for the DEVINTEL core."""

from __future__ import annotations

from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timezone
from threading import RLock
from typing import Any, Callable


@dataclass(frozen=True)
class RuntimeEvent:
    name: str
    payload: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


Handler = Callable[[RuntimeEvent], None]


class EventBus:
    """Synchronous event bus with bounded history and isolated handlers."""

    def __init__(self, history_limit: int = 1000) -> None:
        if history_limit < 1:
            raise ValueError("history_limit must be positive")
        self._handlers: dict[str, list[Handler]] = defaultdict(list)
        self._history: deque[RuntimeEvent] = deque(maxlen=history_limit)
        self._lock = RLock()

    def subscribe(self, name: str, handler: Handler) -> None:
        if not name or not callable(handler):
            raise ValueError("event name and callable handler are required")
        with self._lock:
            if handler not in self._handlers[name]:
                self._handlers[name].append(handler)

    def publish(self, event: RuntimeEvent) -> list[Exception]:
        with self._lock:
            self._history.append(event)
            handlers = tuple(self._handlers.get(event.name, ()))
        errors: list[Exception] = []
        for handler in handlers:
            try:
                handler(event)
            except Exception as exc:  # handlers must not take down the runtime
                errors.append(exc)
        return errors

    def history(self) -> tuple[RuntimeEvent, ...]:
        with self._lock:
            return tuple(self._history)
