"""Stable contracts for DEVINTEL truth, threat, and security state."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timezone
from typing import Mapping


class SecurityState(str, Enum):
    NORMAL = "S0_NORMAL"
    WATCH = "S1_WATCH"
    RESTRICTED = "S2_RESTRICTED"
    CONTAINMENT = "S3_CONTAINMENT"
    RECOVERY = "S4_RECOVERY"
    RESTORED = "S5_RESTORED"
    SAFE_DEGRADED = "S6_SAFE_DEGRADED"


class ThreatLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


@dataclass(frozen=True)
class SecurityEvent:
    kind: str
    level: ThreatLevel
    scope: str
    reason: str
    source: str = "internal"
    metadata: Mapping[str, str] = field(default_factory=dict)
    occurred_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self) -> None:
        if not self.kind.strip() or not self.scope.strip() or not self.reason.strip():
            raise ValueError("security event kind, scope, and reason are required")
        if self.occurred_at.tzinfo is None:
            raise ValueError("occurred_at must be timezone-aware")


@dataclass(frozen=True)
class ContainmentRecord:
    scope: str
    previous_state: SecurityState
    state: SecurityState
    revoked_capabilities: tuple[str, ...] = ()
    reason: str = ""
    verified: bool = False


@dataclass(frozen=True)
class RecoveryRecord:
    scope: str
    state: SecurityState
    verified: bool
    checks: tuple[str, ...] = ()
    reason: str = ""
