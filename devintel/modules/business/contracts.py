"""Opportunity & Business contracts.

Business intelligence is deliberately separated from authority: discovering a
commercial opportunity never grants permission to spend, charge, withdraw, or
enter an agreement.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Mapping


class CommercialRisk(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class RevenueStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    REFUNDED = "refunded"
    FAILED = "failed"


@dataclass(frozen=True)
class BusinessOpportunity:
    title: str
    need: str
    evidence_urls: tuple[str, ...] = ()
    confidence: float = 0.0
    relevance: float = 0.0
    value_score: float = 0.0
    risk: CommercialRisk = CommercialRisk.LOW
    metadata: Mapping[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.title.strip() or not self.need.strip():
            raise ValueError("title and need are required")
        for value in (self.confidence, self.relevance, self.value_score):
            if not 0.0 <= value <= 1.0:
                raise ValueError("scores must be between 0 and 1")
        if not self.evidence_urls:
            raise ValueError("at least one evidence URL is required")


@dataclass(frozen=True)
class ProductOffer:
    opportunity_id: str
    name: str
    description: str
    price_minor: int
    currency: str
    provider: str = ""
    metadata: Mapping[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.opportunity_id.strip() or not self.name.strip():
            raise ValueError("opportunity_id and name are required")
        if not self.description.strip() or self.price_minor < 0:
            raise ValueError("invalid offer")
        if len(self.currency.strip()) != 3:
            raise ValueError("currency must be a 3-letter code")


@dataclass(frozen=True)
class RevenueRecord:
    transaction_id: str
    offer_id: str
    amount_minor: int
    currency: str
    status: RevenueStatus
    occurred_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    provider: str = ""
    metadata: Mapping[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.transaction_id.strip() or not self.offer_id.strip():
            raise ValueError("transaction_id and offer_id are required")
        if self.amount_minor < 0:
            raise ValueError("amount_minor cannot be negative")
        if len(self.currency.strip()) != 3:
            raise ValueError("currency must be a 3-letter code")
        if self.occurred_at.tzinfo is None:
            raise ValueError("occurred_at must be timezone-aware")


@dataclass(frozen=True)
class CommercialActionRequest:
    action: str
    scope_id: str
    risk: CommercialRisk
    reason: str
    requires_owner_approval: bool = True

    def __post_init__(self) -> None:
        if not self.action.strip() or not self.scope_id.strip() or not self.reason.strip():
            raise ValueError("action, scope_id, and reason are required")
        if self.risk in (CommercialRisk.HIGH, CommercialRisk.CRITICAL) and not self.requires_owner_approval:
            raise ValueError("high-risk commercial actions require owner approval")
