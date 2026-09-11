"""Research specialist engine exposed through DEVINTEL's plugin boundary."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from ..plugins.contracts import PluginAction, PluginManifest, PluginRisk
from ..plugins.service import PluginService
from ..research.contracts import ResearchCandidate, ResearchDocument
from ..research.pipeline import ResearchBatch, ResearchPipeline


@dataclass(frozen=True)
class ResearchSpecialistResult:
    """Scoped result returned by the research specialist."""

    scope_id: str
    query: str
    batch: ResearchBatch


class ResearchSource(Protocol):
    def discover(self, query: str) -> list[ResearchCandidate]: ...
    def ingest(self, candidate: ResearchCandidate) -> ResearchDocument: ...


class ResearchSpecialist:
    """Bounded research capability; publishing and other authority stay elsewhere."""

    plugin_id = "specialist.research"

    def __init__(self, plugins: PluginService | None = None, pipeline: ResearchPipeline | None = None) -> None:
        self.plugins = plugins or PluginService()
        self.pipeline = pipeline or ResearchPipeline()
        self.plugins.register(
            PluginManifest(
                plugin_id=self.plugin_id,
                name="Research Specialist",
                version="1.0.0",
                description="Discovers and ingests bounded research candidates for a scoped intelligence task.",
                capabilities=("research.discover", "research.ingest"),
                required_permissions=("research.read",),
                risk=PluginRisk.LOW,
            )
        )
        self.attach()

    def execute(self, scope_id: str, query: str, provider: ResearchSource) -> ResearchSpecialistResult:
        scope = scope_id.strip() if isinstance(scope_id, str) else ""
        search = query.strip() if isinstance(query, str) else ""
        if not scope:
            raise ValueError("scope_id is required")
        if not search:
            raise ValueError("query is required")
        if not hasattr(provider, "discover") or not hasattr(provider, "ingest"):
            raise TypeError("provider must implement discover and ingest")

        action = PluginAction(
            plugin_id=self.plugin_id,
            action="research.scan",
            scope_id=scope,
            risk=PluginRisk.LOW,
            reason="bounded research discovery and ingestion",
            payload={"query": search, "provider": provider},
        )
        result = self.plugins.execute(action)
        if not result.success:
            raise RuntimeError(result.error)
        return ResearchSpecialistResult(scope, search, result.output)

    def attach(self) -> None:
        """Attach the host-controlled research executor to the plugin boundary."""
        def run(action: PluginAction) -> ResearchBatch:
            payload = action.payload
            if not isinstance(payload, dict):
                raise TypeError("research action payload must be a mapping")
            provider = payload.get("provider")
            query = payload.get("query")
            if not isinstance(query, str) or not query.strip():
                raise ValueError("research query is required")
            if not hasattr(provider, "discover") or not hasattr(provider, "ingest"):
                raise TypeError("research provider is invalid")
            return self.pipeline.run(provider, query.strip())

        self.plugins.attach(self.plugin_id, run)
