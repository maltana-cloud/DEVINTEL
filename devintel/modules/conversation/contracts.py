"""Stable contracts for conversation context and bounded memory."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Mapping
from uuid import uuid4


class ConversationScope(str, Enum):
    OWNER = "owner"
    PRIVATE = "private"
    COMMUNITY = "community"
    CHANNEL = "channel"
    GROUP = "group"


class MemoryKind(str, Enum):
    FACT = "fact"
    PREFERENCE = "preference"
    CONTEXT = "context"
    SUMMARY = "summary"
    DECISION = "decision"


@dataclass(frozen=True)
class ConversationMessage:
    scope_id: str
    scope: ConversationScope
    sender_id: str
    text: str
    message_id: str = field(default_factory=lambda: str(uuid4()))
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Mapping[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.scope_id.strip() or not self.sender_id.strip():
            raise ValueError("scope_id and sender_id are required")
        if not self.text.strip():
            raise ValueError("message text is required")
        if self.created_at.tzinfo is None:
            raise ValueError("created_at must be timezone-aware")


@dataclass(frozen=True)
class MemoryEntry:
    scope_id: str
    scope: ConversationScope
    kind: MemoryKind
    content: str
    confidence: float = 0.5
    source_message_id: str | None = None
    memory_id: str = field(default_factory=lambda: str(uuid4()))
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Mapping[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.scope_id.strip() or not self.content.strip():
            raise ValueError("scope_id and content are required")
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("confidence must be between 0 and 1")
        if self.created_at.tzinfo is None:
            raise ValueError("created_at must be timezone-aware")
