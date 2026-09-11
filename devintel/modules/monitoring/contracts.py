"""Stable contracts for System #10 monitoring and owner control."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Mapping


class HealthState(str, Enum):
    HEALTHY = "HEALTHY"
    DEGRADED = "DEGRADED"
    FAILED = "FAILED"
    UNKNOWN = "UNKNOWN"


class AlertSeverity(str, Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"


@dataclass(frozen=True)
class HealthCheck:
    component: str
    scope_id: str
    state: HealthState
    message: str = ""
    observed_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Mapping[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.component.strip() or not self.scope_id.strip():
            raise ValueError("component and scope_id are required")
        if self.observed_at.tzinfo is None:
            raise ValueError("observed_at must be timezone-aware")


@dataclass(frozen=True)
class QueueSnapshot:
    name: str
    scope_id: str
    pending: int = 0
    failed: int = 0
    oldest_age_seconds: float = 0.0

    def __post_init__(self) -> None:
        if not self.name.strip() or not self.scope_id.strip():
            raise ValueError("queue name and scope_id are required")
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
        if not self.alert_id.strip() or not self.scope_id.strip() or not self.title.strip() or not self.message.strip():
            raise ValueError("alert id, scope, title, and message are required")
        if self.created_at.tzinfo is None:
            raise ValueError("created_at must be timezone-aware")


@dataclass(frozen=True)
class OwnerReport:
    scope_id: str
    health: tuple[HealthCheck, ...]
    queues: tuple[QueueSnapshot, ...]
    alerts: tuple[Alert, ...]
    security_events: int = 0
    errors: int = 0
    revenue_records: int = 0
