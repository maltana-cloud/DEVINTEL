"""Strategy and reinvestment specialist behind the plugin boundary."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Protocol, Sequence
from ..strategy.contracts import DomainScore, StrategyDecision
from ..strategy.engine import StrategyEngine
from ..strategy.store import InMemoryStrategyStore
from ..plugins.contracts import PluginAction, PluginManifest, PluginRisk
from ..plugins.service import PluginService

@dataclass(frozen=True)
class StrategySpecialistResult:
    scope_id: str
    decisions: tuple[StrategyDecision, ...]

class StrategySource(Protocol):
    def discover_domains(self, query: str) -> Sequence[DomainScore]: ...

class StrategySpecialist:
    plugin_id = "specialist.strategy"
    def __init__(self, plugins: PluginService | None = None, engine: StrategyEngine | None = None) -> None:
        self.plugins = plugins or PluginService()
        self.engine = engine or StrategyEngine(InMemoryStrategyStore())
        self.plugins.register(PluginManifest(self.plugin_id, "Strategy Specialist", "1.0.0", "Evaluates domains and recommends resource strategy without executing commitments.", ("strategy.evaluate", "strategy.recommend"), ("strategy.read",), PluginRisk.LOW))
        self.attach()
    def attach(self) -> None:
        def run(action: PluginAction) -> StrategySpecialistResult:
            payload = action.payload
            if not isinstance(payload, dict): raise TypeError("strategy action payload must be a mapping")
            source, query = payload.get("source"), payload.get("query")
            if not hasattr(source, "discover_domains"): raise TypeError("strategy source is invalid")
            if not isinstance(query, str) or not query.strip(): raise ValueError("strategy query is required")
            domains = tuple(source.discover_domains(query.strip()))
            if not all(isinstance(item, DomainScore) for item in domains): raise TypeError("strategy source returned invalid domain")
            scoped = tuple(item for item in domains if item.scope_id == action.scope_id)
            decisions = tuple(self.engine.evaluate_domain(item) for item in scoped)
            return StrategySpecialistResult(action.scope_id, decisions)
        self.plugins.attach(self.plugin_id, run)
    def execute(self, scope_id: str, query: str, source: StrategySource) -> StrategySpecialistResult:
        scope = scope_id.strip() if isinstance(scope_id, str) else ""
        search = query.strip() if isinstance(query, str) else ""
        if not scope: raise ValueError("scope_id is required")
        if not search: raise ValueError("query is required")
        if not hasattr(source, "discover_domains"): raise TypeError("source must implement discover_domains")
        result = self.plugins.execute(PluginAction(self.plugin_id, "strategy.scan", scope, PluginRisk.LOW, "bounded strategy discovery", payload={"query": search, "source": source}))
        if not result.success: raise RuntimeError(result.error)
        return result.output
