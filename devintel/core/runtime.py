"""Runtime context and safe execution registry."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from threading import RLock
from typing import Any, Callable

from .events import EventBus
from .permissions import PermissionPolicy
from .state import StateStore

Handler = Callable[[dict[str, Any]], Any]


@dataclass
class RuntimeContext:
    """Dependencies shared by the core without global mutable state."""

    events: EventBus = field(default_factory=EventBus)
    state: StateStore = field(default_factory=StateStore)
    permissions: PermissionPolicy = field(default_factory=PermissionPolicy)
    metrics: Counter[str] = field(default_factory=Counter)
    _handlers: dict[str, Handler] = field(default_factory=dict, init=False, repr=False)
    _lock: RLock = field(default_factory=RLock, init=False, repr=False)

    def register(self, action: str, handler: Handler) -> None:
        if not isinstance(action, str) or not action.strip() or not callable(handler):
            raise ValueError("action and callable handler are required")
        with self._lock:
            if action in self._handlers:
                raise ValueError(f"handler already registered: {action}")
            self._handlers[action] = handler

    def handler(self, action: str) -> Handler | None:
        with self._lock:
            return self._handlers.get(action)

    def increment(self, metric: str) -> None:
        if not isinstance(metric, str) or not metric.strip():
            raise ValueError("metric name is required")
        with self._lock:
            self.metrics[metric] += 1

    def snapshot_metrics(self) -> dict[str, int]:
        with self._lock:
            return dict(self.metrics)
