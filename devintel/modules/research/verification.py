"""Explicit provenance and verification hooks for research evidence.

This layer never claims that a document is true merely because it was ingested.
It verifies structural evidence requirements and leaves substantive fact-checking
to replaceable verifiers.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from .contracts import ResearchDocument, ResearchObservation, canonicalize_url


@dataclass(frozen=True)
class VerificationResult:
    verified: bool
    confidence: float
    reasons: tuple[str, ...] = ()
    evidence_urls: tuple[str, ...] = ()


class ResearchVerifier(Protocol):
    def verify(self, document: ResearchDocument, observation: ResearchObservation) -> VerificationResult: ...


class ProvenanceVerifier:
    """Conservative baseline verifier for evidence/provenance completeness."""

    def verify(self, document: ResearchDocument, observation: ResearchObservation) -> VerificationResult:
        reasons: list[str] = []
        evidence: list[str] = []
        for url in observation.evidence:
            try:
                evidence.append(canonicalize_url(url))
            except ValueError:
                reasons.append("invalid evidence URL")
        if not evidence:
            reasons.append("no evidence URL supplied")
        if canonicalize_url(document.url) not in evidence:
            reasons.append("document URL is not included in evidence")
        if not document.publisher.strip():
            reasons.append("publisher provenance is missing")
        verified = not reasons
        confidence = observation.confidence if verified else min(observation.confidence, 0.49)
        return VerificationResult(verified, confidence, tuple(reasons), tuple(dict.fromkeys(evidence)))
