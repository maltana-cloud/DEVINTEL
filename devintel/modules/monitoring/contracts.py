"""Contracts for System #10 monitoring and owner control."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Mapping


class HealthState(str, Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    FAILED = "failed"
    UNKNOWN = "unknown"


class AlertSeverity(str, Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


def _require_scope(scope_id: str) -> None:
    if not isinstance(scope_id, str) or not scope_id.strip():
        raise ValueError("scope_id is required")


def _require_utc(value: datetime) -> None:
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("observed_at/created_at must be timezone-aware")


@dataclass(frozen=True)
class HealthCheck:
    component: str
    scope_id: str
    state: HealthState
    message: str = ""
    observed_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Mapping[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.component, str) or not self.component.strip():
            raise ValueError("component is required")
        _require_scope(self.scope_id)
        _require_utc(self.observed_at)


@dataclass(frozen=True)
class QueueSnapshot:
    name: str
    scope_id: str
    pending: int = 0
    failed: int = 0
    oldest_age_seconds: float = 0.0

    def __post_init__(self) -> None:
        if not isinstance(self.name, str) or not self.name.strip():
            raise ValueError("queue name is required")
        _require_scope(self.scope_id)
        if self.pending < 0 or self.failed < 0 or self.oldest_age_seconds < 0:
            raise ValueError("queue metrics cannot be negative")


@dataclass(frozen=True)
class Alert:
    alert_id: str
    scope_id: str
    severity: AlertSeverity
    title: str
    message: str
    acknowledged: bool = False
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self) -> None:
        if not isinstance(self.alert_id, str) or not self.alert_id.strip():
            raise ValueError("alert_id is required")
        _require_scope(self.scope_id)
        if not isinstance(self.title, str) or not self.title.strip():
            raise ValueError("title is required")
        if not isinstance(self.message, str) or not self.message.strip():
            raise ValueError("message is required")
        _require_utc(self.created_at)


@dataclass(frozen=True)
class OwnerReport:
    scope_id: str
    health: tuple[HealthCheck, ...] = ()
    queues: tuple[QueueSnapshot, ...] = ()
    alerts: tuple[Alert, ...] = ()
    security_events: int = 0
    errors: int = 0
    revenue_records: int = 0

    def __post_init__(self) -> None:
        _require_scope(self.scope_id)
        if min(self.security_events, self.errors, self.revenue_records) < 0:
            raise ValueError("report counters cannot be negative")
