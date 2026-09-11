"""Growth and awareness specialist exposed through the plugin boundary."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, Sequence

from ..growth.contracts import AudienceSignal, AwarenessPlan
from ..growth.engine import GrowthEngine
from ..plugins.contracts import PluginAction, PluginManifest, PluginRisk
from ..plugins.service import PluginService

@dataclass(frozen=True)
class GrowthSpecialistResult:
    scope_id: str
    plans: tuple[AwarenessPlan, ...]

class GrowthSource(Protocol):
    def discover_signals(self, query: str) -> Sequence[AudienceSignal]: ...

class GrowthSpecialist:
    plugin_id = "specialist.growth"
    def __init__(self, plugins: PluginService | None = None, engine: GrowthEngine | None = None) -> None:
        self.plugins = plugins or PluginService()
        self.engine = engine or GrowthEngine()
        self.plugins.register(PluginManifest(self.plugin_id, "Growth Specialist", "1.1.0", "Discovers scoped audience needs and creates useful awareness plans.", ("growth.discover", "growth.plan"), ("growth.read",), PluginRisk.LOW))
        self.attach()
    def attach(self) -> None:
        def run(action: PluginAction) -> GrowthSpecialistResult:
            payload = action.payload
            if not isinstance(payload, dict): raise TypeError("growth action payload must be a mapping")
            source, query = payload.get("source"), payload.get("query")
            if not hasattr(source, "discover_signals"): raise TypeError("growth source is invalid")
            if not isinstance(query, str) or not query.strip(): raise ValueError("growth query is required")
            signals = tuple(source.discover_signals(query.strip()))
            scoped = tuple(signal for signal in signals if signal.scope_id == action.scope_id)
            plans = tuple(self.engine.plan(self.engine.evaluate(signal), ()) for signal in scoped)
            return GrowthSpecialistResult(action.scope_id, plans)
        self.plugins.attach(self.plugin_id, run)
    def execute(self, scope_id: str, query: str, source: GrowthSource) -> GrowthSpecialistResult:
        if not isinstance(scope_id, str) or not scope_id.strip(): raise ValueError("scope_id is required")
        if not isinstance(query, str) or not query.strip(): raise ValueError("query is required")
        if not hasattr(source, "discover_signals"): raise TypeError("source must implement discover_signals")
        result = self.plugins.execute(PluginAction(self.plugin_id, "growth.scan", scope_id.strip(), PluginRisk.LOW, "bounded growth discovery", {"query": query.strip(), "source": source}))
        if not result.success: raise RuntimeError(result.error)
        return result.output
