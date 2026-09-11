"""Reinvestment and strategy contracts.

Strategy produces recommendations. It never grants authority to spend money,
change security policy, or commit resources without explicit permission.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Mapping


class InvestmentAction(str, Enum):
    HOLD = "hold"
    REINVEST = "reinvest"
    EXPAND = "expand"
    RETIRE = "retire"
    RESEARCH = "research"


@dataclass(frozen=True)
class CostRecord:
    cost_id: str
    scope_id: str
    amount_minor: int
    currency: str
    category: str
    occurred_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    provider: str = ""
    metadata: Mapping[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.cost_id.strip() or not self.scope_id.strip() or not self.category.strip():
            raise ValueError("cost_id, scope_id, and category are required")
        if self.amount_minor < 0:
            raise ValueError("amount_minor cannot be negative")
        if len(self.currency.strip()) != 3:
            raise ValueError("currency must be a 3-letter code")
        if self.occurred_at.tzinfo is None:
            raise ValueError("occurred_at must be timezone-aware")


@dataclass(frozen=True)
class Budget:
    scope_id: str
    amount_minor: int
    currency: str
    period: str

    def __post_init__(self) -> None:
        if not self.scope_id.strip() or not self.period.strip():
            raise ValueError("scope_id and period are required")
        if self.amount_minor < 0:
            raise ValueError("budget cannot be negative")
        if len(self.currency.strip()) != 3:
            raise ValueError("currency must be a 3-letter code")


@dataclass(frozen=True)
class DomainScore:
    scope_id: str
    domain: str
    value: float
    confidence: float
    demand: float
    cost_efficiency: float
    strategic_fit: float
    reason: str

    def __post_init__(self) -> None:
        if not self.scope_id.strip() or not self.domain.strip() or not self.reason.strip():
            raise ValueError("scope_id, domain, and reason are required")
        for value in (self.value, self.confidence, self.demand, self.cost_efficiency, self.strategic_fit):
            if not 0.0 <= value <= 1.0:
                raise ValueError("scores must be between 0 and 1")


@dataclass(frozen=True)
class StrategyDecision:
    scope_id: str
    action: InvestmentAction
    target: str
    rationale: str
    score: float
    requires_owner_approval: bool = True

    def __post_init__(self) -> None:
        if not self.scope_id.strip() or not self.target.strip() or not self.rationale.strip():
            raise ValueError("scope_id, target, and rationale are required")
        if not 0.0 <= self.score <= 1.0:
            raise ValueError("score must be between 0 and 1")
        if self.action in (InvestmentAction.REINVEST, InvestmentAction.EXPAND) and not self.requires_owner_approval:
            raise ValueError("resource commitments require owner approval")
