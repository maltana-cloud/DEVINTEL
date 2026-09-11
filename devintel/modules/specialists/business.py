"""Business intelligence specialist behind DEVINTEL's plugin boundary."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Protocol, Sequence
from ..business.contracts import BusinessOpportunity
from ..business.service import BusinessService
from ..plugins.contracts import PluginAction, PluginManifest, PluginRisk
from ..plugins.service import PluginService

@dataclass(frozen=True)
class BusinessSpecialistResult:
    scope_id: str
    opportunities: tuple[BusinessOpportunity, ...]

class BusinessSource(Protocol):
    def discover_business_opportunities(self, query: str) -> Sequence[BusinessOpportunity]: ...

class BusinessSpecialist:
    plugin_id = "specialist.business"
    def __init__(self, plugins: PluginService | None = None, service: BusinessService | None = None) -> None:
        self.plugins = plugins or PluginService(); self.service = service or BusinessService()
        self.plugins.register(PluginManifest(self.plugin_id, "Business Specialist", "1.0.2", "Finds evidence-backed commercial opportunities without allowing revenue to override truth or relevance.", ("business.discover", "business.rank"), ("business.read",), PluginRisk.LOW))
        self.attach()
    def execute(self, scope_id: str, query: str, source: BusinessSource) -> BusinessSpecialistResult:
        scope = scope_id.strip() if isinstance(scope_id, str) else ""
        search = query.strip() if isinstance(query, str) else ""
        if not scope: raise ValueError("scope_id is required")
        if not search: raise ValueError("query is required")
        if not hasattr(source, "discover_business_opportunities"): raise TypeError("source must implement discover_business_opportunities")
        result = self.plugins.execute(PluginAction(self.plugin_id, "business.scan", scope, PluginRisk.LOW, "bounded business discovery", payload={"query": search, "source": source}))
        if not result.success: raise RuntimeError(result.error)
        return result.output
    def attach(self) -> None:
        def run(action: PluginAction) -> BusinessSpecialistResult:
            payload = action.payload
            if not isinstance(payload, dict): raise TypeError("business action payload must be a mapping")
            source, query = payload.get("source"), payload.get("query")
            if not hasattr(source, "discover_business_opportunities"): raise TypeError("business source is invalid")
            if not isinstance(query, str) or not query.strip(): raise ValueError("business query is required")
            candidates = tuple(source.discover_business_opportunities(query.strip()))
            if not all(isinstance(item, BusinessOpportunity) for item in candidates): raise TypeError("business source returned invalid opportunity")
            accepted = tuple(item for item in candidates if self.service.discover(item))
            ranked = tuple(self.service.ranked_opportunities())
            return BusinessSpecialistResult(action.scope_id, ranked if ranked else accepted)
        self.plugins.attach(self.plugin_id, run)
