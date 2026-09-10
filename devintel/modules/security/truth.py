"""Conservative truth assessment: provenance, agreement, contradiction, uncertainty."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from ..research.contracts import canonicalize_url


@dataclass(frozen=True)
class ClaimAssessment:
    verified: bool
    confidence: float
    reasons: tuple[str, ...] = ()
    evidence_urls: tuple[str, ...] = ()
    contradiction: bool = False


class TruthEngine:
    """Deterministic baseline; it never upgrades weak evidence into certainty."""

    def assess(
        self,
        claim: str,
        evidence_urls: Iterable[str],
        source_confidences: Iterable[float],
        contradictory: bool = False,
    ) -> ClaimAssessment:
        if not claim or not claim.strip():
            raise ValueError("claim is required")
        urls: list[str] = []
        reasons: list[str] = []
        for raw in evidence_urls:
            try:
                urls.append(canonicalize_url(raw))
            except ValueError:
                reasons.append("invalid evidence URL")
        values = [max(0.0, min(1.0, float(v))) for v in source_confidences]
        if not urls:
            reasons.append("no usable evidence")
        if not values:
            reasons.append("no source confidence supplied")
        if contradictory:
            reasons.append("conflicting evidence detected")
        base = min(values) if values else 0.0
        if contradictory:
            base = min(base, 0.49)
        verified = bool(urls and values) and not contradictory
        if reasons and not verified:
            base = min(base, 0.49)
        return ClaimAssessment(
            verified=verified,
            confidence=round(base, 6),
            reasons=tuple(dict.fromkeys(reasons)),
            evidence_urls=tuple(dict.fromkeys(urls)),
            contradiction=contradictory,
        )
