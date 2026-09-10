"""Provider-isolated research pipeline.

Providers supply data only. The pipeline owns bounds, normalization,
deduplication, storage, and observation creation.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from .contracts import ResearchCandidate, ResearchDocument, ResearchObservation
from .limits import ResearchLimits
from .normalization import normalize_content, normalize_title
from .store import ResearchStore


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


class ResearchPipeline:
    """Runs bounded DISCOVER -> INGEST -> NORMALIZE -> DEDUPLICATE -> STORE."""

    def __init__(self, store: ResearchStore | None = None, limits: ResearchLimits | None = None) -> None:
        self.store = store or InMemoryResearchStore()
        self.limits = limits or ResearchLimits()

    def run(self, provider: SourceProvider, query: str) -> ResearchBatch:
        if not isinstance(query, str) or not query.strip():
            raise ValueError("query is required")
        candidates = provider.discover(query.strip())
        if not isinstance(candidates, list):
            raise TypeError("provider.discover must return a list")
        discovered = min(len(candidates), self.limits.max_candidates)
        invalid = 0
        failures = 0
        ingested = duplicates = stored = 0
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
        observation = ResearchObservation(document_url=document.url, kind=kind, value=value, confidence=confidence, evidence=evidence)
        self.store.add_observation(observation)
        return observation


# Imported lazily here to keep the public constructor dependency-light.
from .store import InMemoryResearchStore
