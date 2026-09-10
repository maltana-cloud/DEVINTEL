"""Opportunity discovery contracts and evidence-based scoring."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class OpportunityCandidate:
    title: str
    need: str
    evidence_urls: tuple[str, ...] = ()
    demand_score: float = 0.0
    confidence: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.title, str) or not self.title.strip():
            raise ValueError("opportunity title is required")
        if not isinstance(self.need, str) or not self.need.strip():
            raise ValueError("opportunity need is required")
        for name in ("demand_score", "confidence"):
            value = float(getattr(self, name))
            if not 0.0 <= value <= 1.0:
                raise ValueError(f"{name} must be between 0 and 1")
            object.__setattr__(self, name, value)

    @property
    def value_score(self) -> float:
        """Useful prioritization score; deliberately independent of revenue."""
        evidence = min(1.0, len(self.evidence_urls) / 3.0)
        return round((self.demand_score * 0.55) + (self.confidence * 0.30) + (evidence * 0.15), 4)
