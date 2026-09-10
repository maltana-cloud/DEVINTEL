"""Conversation context engine; response generation remains provider-independent."""

from __future__ import annotations

from dataclasses import dataclass
from threading import RLock
from typing import Callable

from .contracts import ConversationMessage, ConversationScope, MemoryEntry, MemoryKind
from .memory import InMemoryMemoryStore, MemoryStore


@dataclass(frozen=True)
class ConversationResponse:
    text: str
    scope_id: str
    memory: tuple[MemoryEntry, ...] = ()


Responder = Callable[[str, tuple[ConversationMessage, ...], tuple[MemoryEntry, ...]], str]


class ConversationEngine:
    """Maintains bounded context and retrieves only memory from the active scope."""

    def __init__(self, memory: MemoryStore | None = None, *, context_limit: int = 20) -> None:
        if context_limit < 1:
            raise ValueError("context_limit must be positive")
        self.memory = memory or InMemoryMemoryStore()
        self.context_limit = context_limit
        self._contexts: dict[str, list[ConversationMessage]] = {}
        self._lock = RLock()

    def add_message(self, message: ConversationMessage) -> ConversationMessage:
        with self._lock:
            context = self._contexts.setdefault(message.scope_id, [])
            context.append(message)
            del context[:-self.context_limit]
        return message

    def context(self, scope_id: str, limit: int | None = None) -> tuple[ConversationMessage, ...]:
        if not scope_id.strip():
            raise ValueError("scope_id is required")
        count = self.context_limit if limit is None else limit
        if count < 1:
            raise ValueError("limit must be positive")
        with self._lock:
            return tuple(self._contexts.get(scope_id, ())[-count:])

    def remember(self, entry: MemoryEntry) -> MemoryEntry:
        return self.memory.add(entry)

    def respond(self, message: ConversationMessage, responder: Responder) -> ConversationResponse:
        self.add_message(message)
        memories = self.memory.search(message.scope_id, message.text, limit=10)
        reply = responder(message.text, self.context(message.scope_id), memories)
        if not isinstance(reply, str) or not reply.strip():
            raise ValueError("responder must return non-empty text")
        return ConversationResponse(reply.strip(), message.scope_id, memories)

    def remember_summary(self, scope_id: str, scope: ConversationScope, summary: str, *, confidence: float = 0.7) -> MemoryEntry:
        return self.remember(MemoryEntry(scope_id, scope, MemoryKind.SUMMARY, summary, confidence=confidence))
