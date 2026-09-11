"""Thread-safe, bounded monitoring state."""
from __future__ import annotations

from collections import defaultdict, deque
from threading import RLock
from typing import Protocol

from .contracts import Alert, HealthCheck, QueueSnapshot


class MonitoringStore(Protocol):
    def add_health(self, item: HealthCheck) -> None: ...
    def add_queue(self, item: QueueSnapshot) -> None: ...
    def add_alert(self, item: Alert) -> None: ...
    def health(self, scope_id: str) -> list[HealthCheck]: ...
    def queues(self, scope_id: str) -> list[QueueSnapshot]: ...
    def alerts(self, scope_id: str) -> list[Alert]: ...


class InMemoryMonitoringStore:
    def __init__(self, max_items: int = 1000) -> None:
        if max_items < 1:
            raise ValueError("max_items must be positive")
        self._max_items = max_items
        self._lock = RLock()
        self._health: dict[str, deque[HealthCheck]] = defaultdict(lambda: deque(maxlen=max_items))
        self._queues: dict[str, deque[QueueSnapshot]] = defaultdict(lambda: deque(maxlen=max_items))
        self._alerts: dict[str, deque[Alert]] = defaultdict(lambda: deque(maxlen=max_items))

    def add_health(self, item: HealthCheck) -> None:
        with self._lock:
            self._health[item.scope_id].append(item)

    def add_queue(self, item: QueueSnapshot) -> None:
        with self._lock:
            self._queues[item.scope_id].append(item)

    def add_alert(self, item: Alert) -> None:
        with self._lock:
            self._alerts[item.scope_id].append(item)

    def health(self, scope_id: str) -> list[HealthCheck]:
        with self._lock:
            return list(self._health.get(scope_id, ()))

    def queues(self, scope_id: str) -> list[QueueSnapshot]:
        with self._lock:
            return list(self._queues.get(scope_id, ()))

    def alerts(self, scope_id: str) -> list[Alert]:
        with self._lock:
            return list(self._alerts.get(scope_id, ()))
