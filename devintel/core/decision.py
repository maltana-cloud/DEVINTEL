"""Deterministic decision and risk/value scoring."""

from __future__ import annotations

from dataclasses import dataclass

from .contracts import ActionRequest, ActionRisk


@dataclass(frozen=True)
class Decision:
    action: str
    allowed: bool
    score: float
    reason: str


class DecisionEngine:
    """Ranks proposed work; it never grants authority by itself."""

    def decide(self, request: ActionRequest, *, value: float = 0.0) -> Decision:
        value = max(0.0, min(1.0, float(value)))
        risk_penalty = {
            ActionRisk.LOW: 0.0,
            ActionRisk.MEDIUM: 0.2,
            ActionRisk.HIGH: 0.6,
            ActionRisk.CRITICAL: 1.0,
        }[request.risk]
        score = round(value - risk_penalty, 4)
        if request.risk in {ActionRisk.HIGH, ActionRisk.CRITICAL}:
            return Decision(request.action, False, score, "owner approval is required")
        if score < 0:
            return Decision(request.action, False, score, "risk outweighs expected value")
        return Decision(request.action, True, score, "action is eligible for permission check")
