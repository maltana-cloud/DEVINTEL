"""Thread-safe, scope-isolated monitoring storage."""
from __future__ import annotations
from threading import RLock
from .contracts import Alert, HealthCheck, QueueSnapshot

class InMemoryMonitoringStore:
    def __init__(self, max_items: int = 4096) -> None:
        if max_items < 1: raise ValueError("max_items must be positive")
        self._max = max_items; self._lock = RLock()
        self._health: dict[tuple[str, str], HealthCheck] = {}
        self._queues: dict[tuple[str, str], QueueSnapshot] = {}
        self._alerts: dict[str, Alert] = {}
    def record_health(self, item: HealthCheck) -> None:
        with self._lock:
            self._health[(item.scope_id, item.component)] = item
    def record_queue(self, item: QueueSnapshot) -> None:
        with self._lock:
            self._queues[(item.scope_id, item.name)] = item
    def record_alert(self, item: Alert) -> None:
        with self._lock:
            self._alerts[item.alert_id] = item
            if len(self._alerts) > self._max:
                del self._alerts[next(iter(self._alerts))]
    def health(self, scope_id: str) -> tuple[HealthCheck, ...]:
        with self._lock: return tuple(v for (s, _), v in self._health.items() if s == scope_id)
    def queues(self, scope_id: str) -> tuple[QueueSnapshot, ...]:
        with self._lock: return tuple(v for (s, _), v in self._queues.items() if s == scope_id)
    def alerts(self, scope_id: str) -> tuple[Alert, ...]:
        with self._lock: return tuple(v for v in self._alerts.values() if v.scope_id == scope_id)
