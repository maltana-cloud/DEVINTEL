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
        if not isinstance(scope_id, str) or not scope_id.strip():
            raise ValueError("scope_id is required")
        if not isinstance(query, str) or not query.strip():
            raise ValueError("query is required")
        if not hasattr(provider, "discover") or not hasattr(provider, "ingest"):
            raise TypeError("provider must implement discover and ingest")

        action = PluginAction(
            plugin_id=self.plugin_id,
            action="research.scan",
            scope_id=scope_id.strip(),
            risk=PluginRisk.LOW,
            reason="bounded research discovery and ingestion",
        )
        authorization = self.plugins.execute(action)
        if not authorization.success:
            raise RuntimeError(authorization.error)
        batch = self.pipeline.run(provider, query.strip())
        return ResearchSpecialistResult(scope_id.strip(), query.strip(), batch)

    def attach(self) -> None:
        """Attach only a host-controlled capability marker; the research pipeline owns execution."""
        self.plugins.attach(self.plugin_id, lambda _: {"capability": "research"})
