"""Community intelligence specialist behind DEVINTEL's plugin boundary."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Protocol
from ..plugins.contracts import PluginAction, PluginManifest, PluginRisk
from ..plugins.service import PluginService

@dataclass(frozen=True)
class CommunitySignal:
    community_id: str
    summary: str
    relevance: float
    confidence: float
    def __post_init__(self) -> None:
        if not self.community_id.strip(): raise ValueError("community_id is required")
        if not self.summary.strip(): raise ValueError("summary is required")
        if not 0.0 <= self.relevance <= 1.0: raise ValueError("relevance must be between 0 and 1")
        if not 0.0 <= self.confidence <= 1.0: raise ValueError("confidence must be between 0 and 1")

@dataclass(frozen=True)
class CommunitySpecialistResult:
    scope_id: str
    signals: tuple[CommunitySignal, ...]

class CommunitySource(Protocol):
    def observe_communities(self, query: str) -> list[CommunitySignal]: ...

class CommunitySpecialist:
    plugin_id = "specialist.community"
    def __init__(self, plugins: PluginService | None = None) -> None:
        self.plugins = plugins or PluginService()
        self.plugins.register(PluginManifest(
            plugin_id=self.plugin_id, name="Community Specialist", version="1.0.0",
            description="Observes bounded community signals without granting participation authority.",
            capabilities=("community.observe", "community.prioritize"),
            required_permissions=("distribution.read",), risk=PluginRisk.LOW,
        ))
        self.attach()

    def execute(self, scope_id: str, query: str, provider: CommunitySource) -> CommunitySpecialistResult:
        scope = scope_id.strip() if isinstance(scope_id, str) else ""
        search = query.strip() if isinstance(query, str) else ""
        if not scope: raise ValueError("scope_id is required")
        if not search: raise ValueError("query is required")
        if not hasattr(provider, "observe_communities"): raise TypeError("provider must implement observe_communities")
        action = PluginAction(self.plugin_id, "community.observe", scope, PluginRisk.LOW,
                              "bounded community observation", payload={"query": search, "provider": provider})
        result = self.plugins.execute(action)
        if not result.success: raise RuntimeError(result.error)
        return CommunitySpecialistResult(scope, result.output)

    def attach(self) -> None:
        def run(action: PluginAction) -> tuple[CommunitySignal, ...]:
            payload = action.payload
            if not isinstance(payload, dict): raise TypeError("community action payload must be a mapping")
            provider, query = payload.get("provider"), payload.get("query")
            if not isinstance(query, str) or not query.strip(): raise ValueError("community query is required")
            if not hasattr(provider, "observe_communities"): raise TypeError("community provider is invalid")
            signals = provider.observe_communities(query.strip())
            if not isinstance(signals, list): raise TypeError("provider must return a list")
            if not all(isinstance(s, CommunitySignal) for s in signals): raise TypeError("provider returned invalid community signal")
            return tuple(sorted(signals, key=lambda s: (s.relevance, s.confidence), reverse=True))
        self.plugins.attach(self.plugin_id, run)
