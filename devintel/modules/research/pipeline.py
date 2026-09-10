"""Provider-isolated research pipeline with explicit verification and scoring."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from .contracts import ResearchCandidate, ResearchDocument, ResearchObservation
from .limits import ResearchLimits
from .normalization import normalize_content, normalize_title
from .store import InMemoryResearchStore, ResearchStore
from .verification import ProvenanceVerifier, ResearchVerifier, VerificationResult


class SourceProvider(Protocol):
    def discover(self, query: str) -> list[ResearchCandidate]: ...
    def ingest(self, candidate: ResearchCandidate) -> ResearchDocument: ...


@dataclass(frozen=True)
class ResearchBatch:
    discovered: int
    ingested: int
    duplicates: int
    stored: int
    invalid_candidates: int = 0
    provider_failures: int = 0
    observations: int = 0
    verified: int = 0
    routed: int = 0


@dataclass(frozen=True)
class ResearchRoute:
    document_url: str
    destination: str
    score: float
    reason: str


class ResearchPipeline:
    """Runs bounded DISCOVER -> INGEST -> NORMALIZE -> DEDUPLICATE -> EXTRACT -> VERIFY -> SCORE -> ROUTE."""

    def __init__(
        self,
        store: ResearchStore | None = None,
        limits: ResearchLimits | None = None,
        verifier: ResearchVerifier | None = None,
    ) -> None:
        self.store = store or InMemoryResearchStore()
        self.limits = limits or ResearchLimits()
        self.verifier = verifier or ProvenanceVerifier()

    def run(self, provider: SourceProvider, query: str) -> ResearchBatch:
        if not isinstance(query, str) or not query.strip():
            raise ValueError("query is required")
        candidates = provider.discover(query.strip())
        if not isinstance(candidates, list):
            raise TypeError("provider.discover must return a list")
        discovered = min(len(candidates), self.limits.max_candidates)
        invalid = failures = ingested = duplicates = stored = 0
        for candidate in candidates[:self.limits.max_candidates]:
            if not isinstance(candidate, ResearchCandidate):
                invalid += 1
                continue
            try:
                document = provider.ingest(candidate)
                if not isinstance(document, ResearchDocument):
                    invalid += 1
                    continue
                title = normalize_title(document.title)
                content = normalize_content(document.content)
                if len(content) > self.limits.max_document_chars:
                    invalid += 1
                    continue
                document = ResearchDocument(
                    document.url, title, content,
                    publisher=document.publisher,
                    published_at=document.published_at,
                    retrieved_at=document.retrieved_at,
                    metadata=dict(document.metadata),
                )
            except Exception:
                failures += 1
                if failures >= self.limits.max_provider_failures:
                    break
                continue
            ingested += 1
            if self.store.add_document(document):
                stored += 1
            else:
                duplicates += 1
        return ResearchBatch(discovered, ingested, duplicates, stored, invalid, failures)

    def extract_observation(
        self,
        document: ResearchDocument,
        *,
        kind: str,
        value: str,
        confidence: float,
        evidence: tuple[str, ...] = (),
    ) -> ResearchObservation:
        observation = ResearchObservation(
            document_url=document.url, kind=kind, value=value,
            confidence=confidence, evidence=evidence,
        )
        self.store.add_observation(observation)
        return observation

    def verify_observation(self, document: ResearchDocument, observation: ResearchObservation) -> VerificationResult:
        return self.verifier.verify(document, observation)

    @staticmethod
    def score_observation(observation: ResearchObservation, verification: VerificationResult) -> float:
        """Conservative score combining observation confidence and provenance quality."""
        evidence_factor = min(1.0, len(verification.evidence_urls) / 3.0)
        score = observation.confidence * 0.55 + verification.confidence * 0.30 + evidence_factor * 0.15
        return round(max(0.0, min(1.0, score)), 4)

    @staticmethod
    def route(document: ResearchDocument, score: float, *, threshold: float = 0.65) -> ResearchRoute:
        if not 0.0 <= threshold <= 1.0:
            raise ValueError("threshold must be between 0 and 1")
        destination = "publish_candidate" if score >= threshold else "research_queue"
        reason = "evidence-backed score meets routing threshold" if destination == "publish_candidate" else "insufficient verified value for publication"
        return ResearchRoute(document.url, destination, round(score, 4), reason)
