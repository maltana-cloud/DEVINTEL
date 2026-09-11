"""Partnership discovery contracts."""
from dataclasses import dataclass

@dataclass(frozen=True)
class PartnershipCandidate:
    partner_id: str
    name: str
    relevance: float
    evidence_urls: tuple[str, ...] = ()
    def __post_init__(self) -> None:
        if not self.partner_id.strip() or not self.name.strip(): raise ValueError("partner_id and name are required")
        if not 0 <= self.relevance <= 1: raise ValueError("relevance must be between 0 and 1")
