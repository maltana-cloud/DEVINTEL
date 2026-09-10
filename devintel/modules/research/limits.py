"""Resource and provider limits for sustainable free-first research."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ResearchLimits:
    """Explicit limits prevent one provider or query from exhausting resources."""

    max_candidates: int = 100
    max_document_chars: int = 500_000
    max_provider_failures: int = 5

    def __post_init__(self) -> None:
        if self.max_candidates < 1:
            raise ValueError("max_candidates must be positive")
        if self.max_document_chars < 1:
            raise ValueError("max_document_chars must be positive")
        if self.max_provider_failures < 1:
            raise ValueError("max_provider_failures must be positive")
