"""Stable contracts shared by DEVINTEL subsystems.

These contracts deliberately contain no provider-specific logic. Modules should
exchange structured records through these interfaces so providers, domains, and
platforms can evolve independently.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Mapping


class ActionRisk(str, Enum):
    AUTOMATIC = "automatic"
    SAFEGUARDED = "safeguarded"
    OWNER_APPROVAL = "owner_approval"
    EMERGENCY_STOP = "emergency_stop"


class SecurityState(str, Enum):
    NORMAL = "S0_NORMAL"
    WATCH = "S1_WATCH"
    RESTRICTED = "S2_RESTRICTED"
    CONTAINMENT = "S3_CONTAINMENT"
    RECOVERY = "S4_RECOVERY"
    RESTORED = "S5_RESTORED"
    SAFE_DEGRADED = "S6_SAFE_DEGRADED"


class ContentKind(str, Enum):
    FACT = "fact"
    ANALYSIS = "analysis"
    OPPORTUNITY = "opportunity"
    QUESTION = "question"
    UPDATE = "update"
    ALERT = "alert"


@dataclass(frozen=True)
class Provenance:
    source: str
    observed_at: datetime
    evidence: str | None = None
    confidence: float = 0.0


@dataclass(frozen=True)
class IntelligenceItem:
    id: str
    title: str
    summary: str
    kind: ContentKind
    provenance: tuple[Provenance, ...] = ()
    topics: tuple[str, ...] = ()
    freshness: float = 0.0
    relevance: float = 0.0
    importance: float = 0.0
    uncertainty: float = 1.0
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class PublishDecision:
    should_publish: bool
    reason: str
    score: float
    not_before: datetime | None = None
    expires_at: datetime | None = None


@dataclass(frozen=True)
class SecurityEvent:
    event_id: str
    detected_at: datetime
    state: SecurityState
    severity: str
    component: str
    description: str
    contained: bool = False
    evidence_ref: str | None = None


def utc_now() -> datetime:
    """Return an explicit UTC timestamp for audit-friendly records."""
    return datetime.now(timezone.utc)
