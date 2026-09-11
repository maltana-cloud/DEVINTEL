"""Monitoring engine: visibility without authority escalation."""
from __future__ import annotations

from dataclasses import dataclass
from .contracts import Alert, AlertSeverity, HealthCheck, HealthState, OwnerReport, QueueSnapshot
from .store import MonitoringStore


@dataclass(frozen=True)
class MonitoringSummary:
    scope_id: str
    health: tuple[HealthCheck, ...]
    queues: tuple[QueueSnapshot, ...]
    alerts: tuple[Alert, ...]


class MonitoringEngine:
    """Collect operational facts and produce owner-visible reports."""

    def __init__(self, store: MonitoringStore) -> None:
        self.store = store

    def record_health(self, item: HealthCheck) -> None:
        self.store.add_health(item)

    def record_queue(self, item: QueueSnapshot) -> None:
        self.store.add_queue(item)

    def alert(self, scope_id: str, severity: AlertSeverity, title: str, message: str, alert_id: str) -> Alert:
        item = Alert(alert_id, scope_id, severity, title, message)
        self.store.add_alert(item)
        return item

    def summary(self, scope_id: str) -> MonitoringSummary:
        return MonitoringSummary(
            scope_id,
            tuple(self.store.health(scope_id)),
            tuple(self.store.queues(scope_id)),
            tuple(self.store.alerts(scope_id)),
        )

    def report(self, scope_id: str, security_events: int = 0, errors: int = 0, revenue_records: int = 0) -> OwnerReport:
        if min(security_events, errors, revenue_records) < 0:
            raise ValueError("report counters cannot be negative")
        summary = self.summary(scope_id)
        return OwnerReport(scope_id, summary.health, summary.queues, summary.alerts, security_events, errors, revenue_records)

    def overall_state(self, scope_id: str) -> HealthState:
        states = {item.state for item in self.store.health(scope_id)}
        if HealthState.FAILED in states:
            return HealthState.FAILED
        if HealthState.DEGRADED in states:
            return HealthState.DEGRADED
        if HealthState.HEALTHY in states:
            return HealthState.HEALTHY
        return HealthState.UNKNOWN
