"""Fail-closed memory safety policy."""
from __future__ import annotations

from dataclasses import dataclass

from .contracts import MemoryEntry


@dataclass(frozen=True)
class MemoryPolicy:
    """Bounds memory without turning remembered text into authority."""
    max_content_chars: int = 4000
    min_confidence: float = 0.0
    allow_decisions: bool = False

    def validate_write(self, entry: MemoryEntry) -> None:
        if len(entry.content) > self.max_content_chars:
            raise ValueError("memory content exceeds policy limit")
        if entry.confidence < self.min_confidence:
            raise ValueError("memory confidence is below policy threshold")
        if entry.kind.value == "decision" and not self.allow_decisions:
            raise PermissionError("decision memories require explicit policy approval")
        if entry.metadata.get("authority", "").lower() in {"true", "yes", "grant"}:
            raise PermissionError("memory cannot grant authority")

    def can_read(self, requested_scope_id: str, entry: MemoryEntry) -> bool:
        return bool(requested_scope_id.strip()) and entry.scope_id == requested_scope_id
