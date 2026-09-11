"""Thread-safe, bounded strategy storage."""
from __future__ import annotations

from threading import RLock
from typing import Protocol

from .contracts import Budget, CostRecord, DomainScore, StrategyDecision


class StrategyStore(Protocol):
    def add_cost(self, record: CostRecord) -> None: ...
    def add_budget(self, budget: Budget) -> None: ...
    def add_domain_score(self, score: DomainScore) -> None: ...
    def add_decision(self, decision: StrategyDecision) -> None: ...
    def costs(self, scope_id: str) -> list[CostRecord]: ...
    def budgets(self, scope_id: str) -> list[Budget]: ...
    def domain_scores(self, scope_id: str) -> list[DomainScore]: ...
    def decisions(self, scope_id: str) -> list[StrategyDecision]: ...


class InMemoryStrategyStore:
    def __init__(self, max_items: int = 1000) -> None:
        if max_items < 1:
            raise ValueError("max_items must be positive")
        self._max = max_items
        self._lock = RLock()
        self._costs: dict[str, list[CostRecord]] = {}
        self._budgets: dict[str, list[Budget]] = {}
        self._domains: dict[str, list[DomainScore]] = {}
        self._decisions: dict[str, list[StrategyDecision]] = {}
        self._cost_ids: set[str] = set()

    def _append(self, bucket: dict[str, list], key: str, value: object) -> None:
        items = bucket.setdefault(key, [])
        items.append(value)
        if len(items) > self._max:
            del items[: len(items) - self._max]

    def add_cost(self, record: CostRecord) -> None:
        with self._lock:
            if record.cost_id in self._cost_ids:
                return
            self._cost_ids.add(record.cost_id)
            self._append(self._costs, record.scope_id, record)

    def add_budget(self, budget: Budget) -> None:
        with self._lock:
            self._append(self._budgets, budget.scope_id, budget)

    def add_domain_score(self, score: DomainScore) -> None:
        with self._lock:
            self._append(self._domains, score.scope_id, score)

    def add_decision(self, decision: StrategyDecision) -> None:
        with self._lock:
            self._append(self._decisions, decision.scope_id, decision)

    def costs(self, scope_id: str) -> list[CostRecord]:
        with self._lock:
            return list(self._costs.get(scope_id, ()))

    def budgets(self, scope_id: str) -> list[Budget]:
        with self._lock:
            return list(self._budgets.get(scope_id, ()))

    def domain_scores(self, scope_id: str) -> list[DomainScore]:
        with self._lock:
            return list(self._domains.get(scope_id, ()))

    def decisions(self, scope_id: str) -> list[StrategyDecision]:
        with self._lock:
            return list(self._decisions.get(scope_id, ()))
