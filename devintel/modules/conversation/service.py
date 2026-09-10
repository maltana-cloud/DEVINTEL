"""Safe conversation facade integrating memory policy, events, and audit."""
from __future__ import annotations

from typing import Callable

from devintel.core.audit import AuditLog, AuditRecord
from devintel.core.events import EventBus, RuntimeEvent

from .contracts import ConversationMessage, ConversationScope, MemoryEntry
from .engine import ConversationEngine, ConversationResponse
from .policy import MemoryPolicy


Responder = Callable[[str, tuple[ConversationMessage, ...], tuple[MemoryEntry, ...]], str]


class ConversationService:
    """Application boundary for conversation and memory operations."""

    def __init__(self, engine: ConversationEngine | None = None, *, policy: MemoryPolicy | None = None,
                 events: EventBus | None = None, audit: AuditLog | None = None) -> None:
        self.engine = engine or ConversationEngine()
        self.policy = policy or MemoryPolicy()
        self.events = events or EventBus()
        self.audit = audit or AuditLog()

    def receive(self, message: ConversationMessage, responder: Responder) -> ConversationResponse:
        self.engine.add_message(message)
        try:
            memories = tuple(m for m in self.engine.memory.search(message.scope_id, message.text, 10)
                             if self.policy.can_read(message.scope_id, m))
            reply = responder(message.text, self.engine.context(message.scope_id), memories)
            if not isinstance(reply, str) or not reply.strip():
                raise ValueError("responder must return non-empty text")
            result = ConversationResponse(reply.strip(), message.scope_id, memories)
            self.events.publish(RuntimeEvent("conversation.responded", {"scope_id": message.scope_id, "message_id": message.message_id}))
            self.audit.record(AuditRecord("conversation.responded", action="respond", success=True,
                                          details={"scope_id": message.scope_id, "message_id": message.message_id}))
            return result
        except Exception as exc:
            self.events.publish(RuntimeEvent("conversation.failed", {"scope_id": message.scope_id, "message_id": message.message_id, "error": type(exc).__name__}))
            self.audit.record(AuditRecord("conversation.failed", action="respond", success=False,
                                          details={"scope_id": message.scope_id, "error": type(exc).__name__}))
            raise

    def remember(self, entry: MemoryEntry) -> MemoryEntry:
        self.policy.validate_write(entry)
        result = self.engine.remember(entry)
        self.events.publish(RuntimeEvent("memory.written", {"scope_id": entry.scope_id, "memory_id": entry.memory_id}))
        self.audit.record(AuditRecord("memory.written", action="remember", success=True,
                                      details={"scope_id": entry.scope_id, "memory_id": entry.memory_id,
                                               "kind": entry.kind.value}))
        return result

    def context(self, scope_id: str, limit: int | None = None) -> tuple[ConversationMessage, ...]:
        return self.engine.context(scope_id, limit)

    def remember_summary(self, scope_id: str, scope: ConversationScope, summary: str, *, confidence: float = 0.7) -> MemoryEntry:
        return self.remember(self.engine.remember_summary(scope_id, scope, summary, confidence=confidence))
