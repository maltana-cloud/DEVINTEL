"""Stable contracts for Growth & Awareness."""
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any


def _text(value: str, name: str) -> str:
    value = str(value).strip()
    if not value:
        raise ValueError(f"{name} must not be empty")
    return value


class SignalKind(str, Enum):
    AUDIENCE_NEED = "audience_need"
    UNANSWERED_QUESTION = "unanswered_question"
    DEMAND = "demand"
    DISTRIBUTION = "distribution"
    PARTNERSHIP = "partnership"
    FEEDBACK = "feedback"


class AwarenessAction(str, Enum):
    NO_ACTION = "no_action"
    RESEARCH = "research"
    EDUCATE = "educate"
    DISTRIBUTE = "distribute"
    PARTNER = "partner"


@dataclass(frozen=True)
class AudienceSignal:
    signal_id: str
    scope_id: str
    kind: SignalKind
    summary: str
    evidence_urls: tuple[str, ...] = ()
    confidence: float = 0.0
    observed_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        _text(self.signal_id, "signal_id"); _text(self.scope_id, "scope_id"); _text(self.summary, "summary")
        if not 0.0 <= self.confidence <= 1.0: raise ValueError("confidence must be between 0 and 1")
        if self.observed_at.tzinfo is None: raise ValueError("observed_at must be timezone-aware")
        for url in self.evidence_urls: _text(url, "evidence_url")


@dataclass(frozen=True)
class GrowthScore:
    value: float
    confidence: float
    reasons: tuple[str, ...] = ()
    def __post_init__(self) -> None:
        if not 0.0 <= self.value <= 1.0 or not 0.0 <= self.confidence <= 1.0:
            raise ValueError("scores must be between 0 and 1")


@dataclass(frozen=True)
class GrowthOpportunity:
    opportunity_id: str
    scope_id: str
    title: str
    need: str
    score: GrowthScore
    action: AwarenessAction
    evidence_urls: tuple[str, ...] = ()
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        _text(self.opportunity_id, "opportunity_id"); _text(self.scope_id, "scope_id"); _text(self.title, "title"); _text(self.need, "need")


@dataclass(frozen=True)
class AwarenessPlan:
    opportunity_id: str
    action: AwarenessAction
    destinations: tuple[str, ...] = ()
    rationale: str = ""

    def __post_init__(self) -> None:
        _text(self.opportunity_id, "opportunity_id")
        if self.action is not AwarenessAction.NO_ACTION and not self.destinations:
            raise ValueError("non-empty destinations required for an awareness action")
