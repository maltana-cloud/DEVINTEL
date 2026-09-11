"""Monitoring orchestration and owner-report generation."""
from __future__ import annotations
from uuid import uuid4
from .contracts import Alert, AlertSeverity, HealthCheck, HealthState, OwnerReport, QueueSnapshot
from .store import InMemoryMonitoringStore

class MonitoringEngine:
    """Observe system state; never grants authority or performs business actions."""
    def __init__(self, store: InMemoryMonitoringStore | None = None) -> None:
        self.store = store or InMemoryMonitoringStore()
    def record_health(self, check: HealthCheck) -> HealthCheck:
        self.store.record_health(check); return check
    def record_queue(self, snapshot: QueueSnapshot) -> QueueSnapshot:
        self.store.record_queue(snapshot); return snapshot
    def alert(self, scope_id: str, severity: AlertSeverity, title: str, message: str) -> Alert:
        item = Alert(uuid4().hex, scope_id, severity, title, message)
        self.store.record_alert(item); return item
    def report(self, scope_id: str, *, security_events: int = 0, errors: int = 0, revenue_records: int = 0) -> OwnerReport:
        if min(security_events, errors, revenue_records) < 0: raise ValueError("report counters cannot be negative")
        return OwnerReport(scope_id, self.store.health(scope_id), self.store.queues(scope_id), self.store.alerts(scope_id), security_events, errors, revenue_records)
    def overall_state(self, scope_id: str) -> HealthState:
        checks = self.store.health(scope_id)
        if not checks: return HealthState.UNKNOWN
        if any(c.state == HealthState.FAILED for c in checks): return HealthState.FAILED
        if any(c.state in (HealthState.DEGRADED, HealthState.UNKNOWN) for c in checks): return HealthState.DEGRADED
        return HealthState.HEALTHY
