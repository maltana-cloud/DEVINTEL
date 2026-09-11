"""Opportunity intelligence specialist behind DEVINTEL's plugin boundary."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Protocol
from ..plugins.contracts import PluginAction, PluginManifest, PluginRisk
from ..plugins.service import PluginService
from ..research.opportunities import OpportunityCandidate

@dataclass(frozen=True)
class OpportunitySpecialistResult:
    scope_id: str
    candidates: tuple[OpportunityCandidate, ...]

class OpportunitySource(Protocol):
    def discover_opportunities(self, query: str) -> list[OpportunityCandidate]: ...

class OpportunitySpecialist:
    plugin_id = "specialist.opportunity"
    def __init__(self, plugins: PluginService | None = None) -> None:
        self.plugins = plugins or PluginService()
        self.plugins.register(PluginManifest(
            plugin_id=self.plugin_id, name="Opportunity Specialist", version="1.0.0",
            description="Finds evidence-backed unmet needs and opportunities within a bounded scope.",
            capabilities=("opportunity.discover", "opportunity.rank"),
            required_permissions=("research.read",), risk=PluginRisk.LOW,
        ))
        self.attach()

    def execute(self, scope_id: str, query: str, provider: OpportunitySource) -> OpportunitySpecialistResult:
        scope = scope_id.strip() if isinstance(scope_id, str) else ""
        search = query.strip() if isinstance(query, str) else ""
        if not scope: raise ValueError("scope_id is required")
        if not search: raise ValueError("query is required")
        if not hasattr(provider, "discover_opportunities"):
            raise TypeError("provider must implement discover_opportunities")
        action = PluginAction(self.plugin_id, "opportunity.scan", scope, PluginRisk.LOW,
                              "bounded opportunity discovery", payload={"query": search, "provider": provider})
        result = self.plugins.execute(action)
        if not result.success: raise RuntimeError(result.error)
        return OpportunitySpecialistResult(scope, result.output)

    def attach(self) -> None:
        def run(action: PluginAction) -> tuple[OpportunityCandidate, ...]:
            payload = action.payload
            if not isinstance(payload, dict): raise TypeError("opportunity action payload must be a mapping")
            provider = payload.get("provider"); query = payload.get("query")
            if not isinstance(query, str) or not query.strip(): raise ValueError("opportunity query is required")
            if not hasattr(provider, "discover_opportunities"): raise TypeError("opportunity provider is invalid")
            candidates = provider.discover_opportunities(query.strip())
            if not isinstance(candidates, list): raise TypeError("provider must return a list")
            valid = tuple(c for c in candidates if isinstance(c, OpportunityCandidate))
            return tuple(sorted(valid, key=lambda c: (c.value_score, c.confidence, c.demand_score), reverse=True))
        self.plugins.attach(self.plugin_id, run)
