"""Provider boundaries for audience and distribution intelligence."""
from typing import Protocol, Sequence
from .contracts import AudienceSignal

class SignalProvider(Protocol):
    def discover(self, scope_id: str, query: str) -> Sequence[AudienceSignal]: ...

class DistributionDiscoveryProvider(Protocol):
    def destinations(self, scope_id: str, signal: AudienceSignal) -> Sequence[str]: ...

class PartnershipProvider(Protocol):
    def candidates(self, scope_id: str, signal: AudienceSignal) -> Sequence["PartnershipCandidate"]: ...

class PartnershipCandidate:
    def __init__(self, partner_id: str, name: str, relevance: float, evidence_urls: tuple[str, ...] = ()) -> None:
        self.partner_id = str(partner_id).strip(); self.name = str(name).strip(); self.relevance = float(relevance); self.evidence_urls = tuple(evidence_urls)
        if not self.partner_id or not self.name: raise ValueError("partner_id and name are required")
        if not 0 <= self.relevance <= 1: raise ValueError("relevance must be between 0 and 1")
