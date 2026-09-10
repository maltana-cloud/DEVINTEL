"""Provider-isolated research pipeline.

Providers only supply candidates/documents. The pipeline owns normalization,
deduplication, storage and observation extraction hooks.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from .contracts import ResearchCandidate, ResearchDocument, ResearchObservation
from .store import InMemoryResearchStore


class SourceProvider(Protocol):
    def discover(self, query: str) -> list[ResearchCandidate]: ...
    def ingest(self, candidate: ResearchCandidate) -> ResearchDocument: ...


@dataclass(frozen=True)
class ResearchBatch:
    discovered: int
    ingested: int
    duplicates: int
    stored: int


class ResearchPipeline:
    """Runs DISCOVER -> INGEST -> NORMALIZE -> DEDUPLICATE -> STORE."""

    def __init__(self, store: InMemoryResearchStore | None = None) -> None:
        self.store = store or InMemoryResearchStore()

    def run(self, provider: SourceProvider, query: str) -> ResearchBatch:
        if not isinstance(query, str) or not query.strip():
            raise ValueError("query is required")
        candidates = provider.discover(query.strip())
        ingested = 0
        duplicates = 0
        stored = 0
        for candidate in candidates:
            if not isinstance(candidate, ResearchCandidate):
                continue
            try:
                document = provider.ingest(candidate)
            except Exception:
                # One bad provider item must not take down the research run.
                continue
            ingested += 1
            if self.store.add_document(document):
                stored += 1
            else:
                duplicates += 1
        return ResearchBatch(len(candidates), ingested, duplicates, stored)

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
            document_url=document.url,
            kind=kind,
            value=value,
            confidence=confidence,
            evidence=evidence,
        )
        self.store.add_observation(observation)
        return observation
