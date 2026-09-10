"""Free-first research store with URL/content deduplication."""

from __future__ import annotations

from threading import RLock

from .contracts import ResearchDocument, ResearchObservation, canonicalize_url


class InMemoryResearchStore:
    """Thread-safe reference store; a persistent backend can implement the same API later."""

    def __init__(self) -> None:
        self._documents: dict[str, ResearchDocument] = {}
        self._content_index: dict[str, str] = {}
        self._observations: list[ResearchObservation] = []
        self._lock = RLock()

    def add_document(self, document: ResearchDocument) -> bool:
        with self._lock:
            url = canonicalize_url(document.url)
            if url in self._documents or document.content_hash in self._content_index:
                return False
            self._documents[url] = document
            self._content_index[document.content_hash] = url
            return True

    def get(self, url: str) -> ResearchDocument | None:
        with self._lock:
            return self._documents.get(canonicalize_url(url))

    def add_observation(self, observation: ResearchObservation) -> None:
        with self._lock:
            self._observations.append(observation)

    def documents(self) -> tuple[ResearchDocument, ...]:
        with self._lock:
            return tuple(self._documents.values())

    def observations(self) -> tuple[ResearchObservation, ...]:
        with self._lock:
            return tuple(self._observations)

    def count_documents(self) -> int:
        with self._lock:
            return len(self._documents)

    def count_observations(self) -> int:
        with self._lock:
            return len(self._observations)
