"""Thread-safe storage with per-scope isolation."""
from threading import RLock
from typing import Protocol
from .contracts import AudienceSignal, GrowthOpportunity

class GrowthStore(Protocol):
    def add_signal(self, signal: AudienceSignal) -> None: ...
    def signals(self, scope_id: str) -> list[AudienceSignal]: ...
    def add_opportunity(self, opportunity: GrowthOpportunity) -> None: ...
    def opportunities(self, scope_id: str) -> list[GrowthOpportunity]: ...

class InMemoryGrowthStore:
    def __init__(self, max_items: int = 1000) -> None:
        if max_items < 1: raise ValueError("max_items must be positive")
        self._max = max_items; self._lock = RLock(); self._signals: dict[str, list[AudienceSignal]] = {}; self._opps: dict[str, list[GrowthOpportunity]] = {}
    def add_signal(self, signal: AudienceSignal) -> None:
        with self._lock:
            items = self._signals.setdefault(signal.scope_id, [])
            if any(x.signal_id == signal.signal_id for x in items): return
            items.append(signal); del items[:-self._max]
    def signals(self, scope_id: str) -> list[AudienceSignal]:
        with self._lock: return list(self._signals.get(scope_id, ()))
    def add_opportunity(self, opportunity: GrowthOpportunity) -> None:
        with self._lock:
            items = self._opps.setdefault(opportunity.scope_id, [])
            if any(x.opportunity_id == opportunity.opportunity_id for x in items): return
            items.append(opportunity); del items[:-self._max]
    def opportunities(self, scope_id: str) -> list[GrowthOpportunity]:
        with self._lock: return list(self._opps.get(scope_id, ()))
