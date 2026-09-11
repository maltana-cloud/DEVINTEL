"""System #9 strategy analytics and recommendation engine."""
from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass

from .contracts import CostRecord, DomainScore, StrategyDecision
from .policy import StrategyPolicy
from .store import StrategyStore


@dataclass(frozen=True)
class StrategySummary:
    scope_id: str
    cost_totals: dict[str, int]
    budget_totals: dict[str, int]
    domain_scores: list[DomainScore]
    decisions: list[StrategyDecision]


class StrategyEngine:
    """Analyze resources and return recommendations without executing them."""

    def __init__(self, store: StrategyStore, policy: StrategyPolicy | None = None) -> None:
        self.store = store
        self.policy = policy or StrategyPolicy()

    def record_cost(self, record: CostRecord) -> None:
        self.store.add_cost(record)

    def record_budget(self, budget) -> None:
        self.store.add_budget(budget)

    def evaluate_domain(self, domain: DomainScore) -> StrategyDecision:
        self.store.add_domain_score(domain)
        decision = self.policy.decide(domain)
        self.store.add_decision(decision)
        return decision

    def summary(self, scope_id: str) -> StrategySummary:
        costs = defaultdict(int)
        for record in self.store.costs(scope_id):
            costs[record.currency] += record.amount_minor
        budgets = defaultdict(int)
        for budget in self.store.budgets(scope_id):
            budgets[budget.currency] += budget.amount_minor
        return StrategySummary(scope_id, dict(costs), dict(budgets), self.store.domain_scores(scope_id), self.store.decisions(scope_id))

    def bottlenecks(self, scope_id: str) -> list[str]:
        costs = self.store.costs(scope_id)
        by_category: dict[str, int] = defaultdict(int)
        for record in costs:
            by_category[record.category] += record.amount_minor
        return [category for category, _ in sorted(by_category.items(), key=lambda item: item[1], reverse=True)]
