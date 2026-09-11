"""Truth and verification specialist behind DEVINTEL's plugin boundary."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Iterable, Protocol

from ..plugins.contracts import PluginAction, PluginManifest, PluginRisk
from ..plugins.service import PluginService
from ..security.truth import ClaimAssessment, TruthEngine

@dataclass(frozen=True)
class TruthSpecialistResult:
    scope_id: str
    claim: str
    assessment: ClaimAssessment

class TruthSource(Protocol):
    def evidence_urls(self, claim: str) -> Iterable[str]: ...
    def source_confidences(self, claim: str) -> Iterable[float]: ...
    def contradictory(self, claim: str) -> bool: ...

class TruthSpecialist:
    """Assesses claims conservatively; verification never grants authority."""
    plugin_id = "specialist.truth"

    def __init__(self, plugins: PluginService | None = None, engine: TruthEngine | None = None) -> None:
        self.plugins = plugins or PluginService()
        self.engine = engine or TruthEngine()
        self.plugins.register(PluginManifest(
            plugin_id=self.plugin_id,
            name="Truth Specialist",
            version="1.0.0",
            description="Conservatively assesses scoped claims using evidence, source confidence, and contradiction signals.",
            capabilities=("truth.assess", "truth.contradiction"),
            required_permissions=("research.read",),
            risk=PluginRisk.LOW,
        ))
        self.attach()

    def execute(self, scope_id: str, claim: str, provider: TruthSource) -> TruthSpecialistResult:
        scope = scope_id.strip() if isinstance(scope_id, str) else ""
        text = claim.strip() if isinstance(claim, str) else ""
        if not scope:
            raise ValueError("scope_id is required")
        if not text:
            raise ValueError("claim is required")
        if not all(hasattr(provider, name) for name in ("evidence_urls", "source_confidences", "contradictory")):
            raise TypeError("provider must implement truth source methods")
        action = PluginAction(
            self.plugin_id, "truth.assess", scope, PluginRisk.LOW,
            "bounded claim verification", payload={"claim": text, "provider": provider},
        )
        result = self.plugins.execute(action)
        if not result.success:
            raise RuntimeError(result.error)
        return TruthSpecialistResult(scope, text, result.output)

    def attach(self) -> None:
        def run(action: PluginAction) -> ClaimAssessment:
            payload = action.payload
            if not isinstance(payload, dict):
                raise TypeError("truth action payload must be a mapping")
            claim = payload.get("claim")
            provider = payload.get("provider")
            if not isinstance(claim, str) or not claim.strip():
                raise ValueError("truth claim is required")
            if not all(hasattr(provider, name) for name in ("evidence_urls", "source_confidences", "contradictory")):
                raise TypeError("truth provider is invalid")
            return self.engine.assess(
                claim,
                provider.evidence_urls(claim),
                provider.source_confidences(claim),
                bool(provider.contradictory(claim)),
            )
        self.plugins.attach(self.plugin_id, run)
