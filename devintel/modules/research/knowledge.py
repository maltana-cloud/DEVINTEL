"""Structured knowledge primitives derived from research evidence."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class Claim:
    """A claim about the world, explicitly separated from its evidence."""

    subject: str
    predicate: str
    object: str
    confidence: float = 0.0
    evidence_urls: tuple[str, ...] = ()
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        for value in (self.subject, self.predicate, self.object):
            if not isinstance(value, str) or not value.strip():
                raise ValueError("claim subject, predicate, and object are required")
        confidence = float(self.confidence)
        if not 0.0 <= confidence <= 1.0:
            raise ValueError("confidence must be between 0 and 1")
        object.__setattr__(self, "confidence", confidence)


@dataclass(frozen=True)
class Entity:
    name: str
    entity_type: str = "unknown"
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.name, str) or not self.name.strip():
            raise ValueError("entity name is required")
        if not isinstance(self.entity_type, str) or not self.entity_type.strip():
            raise ValueError("entity type is required")


@dataclass(frozen=True)
class Relationship:
    source: str
    relation: str
    target: str
    confidence: float = 0.0

    def __post_init__(self) -> None:
        if not all(isinstance(v, str) and v.strip() for v in (self.source, self.relation, self.target)):
            raise ValueError("relationship fields are required")
        confidence = float(self.confidence)
        if not 0.0 <= confidence <= 1.0:
            raise ValueError("confidence must be between 0 and 1")
        object.__setattr__(self, "confidence", confidence)
