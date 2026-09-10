"""Deterministic in-process event bus for the DEVINTEL core."""

from __future__ import annotations

from collections import defaultdict, deque
from dataclasses import dataclass
from threading import RLock
from typing import Any, Callable


@dataclass(frozen=True)
class Event:
    name: str
    payload: Any = None


Handler = Callable[[Event], None]


class EventBus:
    """Small synchronous bus with bounded history and isolated handlers."""

    def __init__(self, history_limit: int = 1000) -> None:
        if history_limit < 1:
            raise ValueError("history_limit must be positive")
        self._handlers: dict[str, list[Handler]] = defaultdict(list)
        self._history: deque[Event] = deque(maxlen=history_limit)
        self._lock = RLock()

    def subscribe(self, name: str, handler: Handler) -> None:
        if not name or not callable(handler):
            raise ValueError("event name and callable handler are required")
        with self._lock:
            if handler not in self._handlers[name]:
                self._handlers[name].append(handler)

    def publish(self, event: Event) -> list[Exception]:
        with self._lock:
            self._history.append(event)
            handlers = tuple(self._handlers.get(event.name, ()))
        errors: list[Exception] = []
        for handler in handlers:
            try:
                handler(event)
            except Exception as exc:  # handler failures must not kill the bus
                errors.append(exc)
        return errors

    def history(self) -> tuple[Event, ...]:
        with self._lock:
            return tuple(self._history)
