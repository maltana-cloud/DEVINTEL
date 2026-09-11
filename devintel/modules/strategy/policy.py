"""Bounded strategy policy."""
from __future__ import annotations

from .contracts import DomainScore, InvestmentAction, StrategyDecision


class StrategyPolicy:
    def __init__(self, min_score: float = 0.60, min_confidence: float = 0.60) -> None:
        if not 0.0 <= min_score <= 1.0 or not 0.0 <= min_confidence <= 1.0:
            raise ValueError("thresholds must be between 0 and 1")
        self.min_score = min_score
        self.min_confidence = min_confidence

    def score(self, domain: DomainScore) -> float:
        return min(1.0, 0.35 * domain.value + 0.20 * domain.confidence + 0.20 * domain.demand + 0.15 * domain.cost_efficiency + 0.10 * domain.strategic_fit)

    def decide(self, domain: DomainScore) -> StrategyDecision:
        score = self.score(domain)
        if domain.confidence < self.min_confidence or score < self.min_score:
            action = InvestmentAction.RESEARCH
            rationale = "insufficient confidence or strategic value for commitment"
        elif domain.cost_efficiency < 0.40:
            action = InvestmentAction.RESEARCH
            rationale = "cost efficiency is too weak for reinvestment"
        elif domain.demand >= 0.75 and domain.cost_efficiency >= 0.70:
            action = InvestmentAction.EXPAND
            rationale = "strong demand and cost efficiency support expansion"
        elif score >= 0.75:
            action = InvestmentAction.REINVEST
            rationale = "strong value, confidence, and strategic fit support reinvestment"
        elif score < 0.50:
            action = InvestmentAction.RETIRE
            rationale = "low strategic value supports retirement review"
        else:
            action = InvestmentAction.HOLD
            rationale = "evidence supports maintaining the current allocation"
        return StrategyDecision(domain.scope_id, action, domain.domain, rationale, score, requires_owner_approval=action in (InvestmentAction.REINVEST, InvestmentAction.EXPAND))

    def authorize(self, decision: StrategyDecision, owner_approved: bool = False) -> bool:
        if decision.action in (InvestmentAction.REINVEST, InvestmentAction.EXPAND):
            return owner_approved
        return decision.action in (InvestmentAction.HOLD, InvestmentAction.RESEARCH, InvestmentAction.RETIRE)
