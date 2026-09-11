"""System #9 strategy analytics and recommendation engine."""
from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from typing import Protocol

from devintel.modules.business.contracts import RevenueRecord, RevenueStatus

from .contracts import Budget, CostRecord, DomainScore, StrategyDecision
from .policy import StrategyPolicy
from .store import StrategyStore


class RevenueSource(Protocol):
    def revenue(self) -> list[RevenueRecord]: ...


@dataclass(frozen=True)
class RevenueSummary:
    confirmed_totals: dict[str, int]
    pending_totals: dict[str, int]
    refunded_totals: dict[str, int]


@dataclass(frozen=True)
class StrategySummary:
    scope_id: str
    cost_totals: dict[str, int]
    budget_totals: dict[str, int]
    revenue: RevenueSummary
    domain_scores: list[DomainScore]
    decisions: list[StrategyDecision]


class StrategyEngine:
    """Analyze resources and return recommendations without executing them."""

    def __init__(self, store: StrategyStore, policy: StrategyPolicy | None = None, revenue_source: RevenueSource | None = None) -> None:
        self.store = store
        self.policy = policy or StrategyPolicy()
        self.revenue_source = revenue_source

    def record_cost(self, record: CostRecord) -> None:
        self.store.add_cost(record)

    def record_budget(self, budget: Budget) -> None:
        self.store.add_budget(budget)

    def evaluate_domain(self, domain: DomainScore) -> StrategyDecision:
        self.store.add_domain_score(domain)
        decision = self.policy.decide(domain)
        self.store.add_decision(decision)
        return decision

    def revenue_summary(self) -> RevenueSummary:
        totals = {RevenueStatus.CONFIRMED: defaultdict(int), RevenueStatus.PENDING: defaultdict(int), RevenueStatus.REFUNDED: defaultdict(int)}
        if self.revenue_source is not None:
            for record in self.revenue_source.revenue():
                if record.status in totals:
                    totals[record.status][record.currency] += record.amount_minor
        return RevenueSummary(dict(totals[RevenueStatus.CONFIRMED]), dict(totals[RevenueStatus.PENDING]), dict(totals[RevenueStatus.REFUNDED]))

    def summary(self, scope_id: str) -> StrategySummary:
        costs = defaultdict(int)
        for record in self.store.costs(scope_id):
            costs[record.currency] += record.amount_minor
        budgets = defaultdict(int)
        for budget in self.store.budgets(scope_id):
            budgets[budget.currency] += budget.amount_minor
        return StrategySummary(scope_id, dict(costs), dict(budgets), self.revenue_summary(), self.store.domain_scores(scope_id), self.store.decisions(scope_id))

    def roi_by_currency(self, scope_id: str) -> dict[str, float]:
        costs = defaultdict(int)
        for record in self.store.costs(scope_id):
            costs[record.currency] += record.amount_minor
        revenue = self.revenue_summary().confirmed_totals
        currencies = set(costs) | set(revenue)
        return {currency: (revenue.get(currency, 0) - costs.get(currency, 0)) / costs[currency] if costs.get(currency, 0) else float("inf") for currency in currencies}

    def bottlenecks(self, scope_id: str) -> list[str]:
        by_category: dict[str, int] = defaultdict(int)
        for record in self.store.costs(scope_id):
            by_category[record.category] += record.amount_minor
        return [category for category, _ in sorted(by_category.items(), key=lambda item: item[1], reverse=True)]
