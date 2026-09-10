from datetime import datetime, timezone

import pytest

from devintel.core.audit import AuditLog
from devintel.core.events import EventBus
from devintel.modules.conversation import (
    ConversationEngine, ConversationMessage, ConversationScope, ConversationService,
    InMemoryMemoryStore, MemoryEntry, MemoryKind, MemoryPolicy, SQLiteMemoryStore,
)


def test_context_is_bounded_and_scoped():
    engine = ConversationEngine(context_limit=2)
    for text in ("one", "two", "three"):
        engine.add_message(ConversationMessage("a", ConversationScope.COMMUNITY, "u", text))
    engine.add_message(ConversationMessage("b", ConversationScope.COMMUNITY, "u", "other"))
    assert [m.text for m in engine.context("a")] == ["two", "three"]
    assert [m.text for m in engine.context("b")] == ["other"]


def test_memory_search_never_crosses_scope():
    store = InMemoryMemoryStore()
    store.add(MemoryEntry("a", ConversationScope.COMMUNITY, MemoryKind.FACT, "Python developer"))
    store.add(MemoryEntry("b", ConversationScope.COMMUNITY, MemoryKind.FACT, "Python developer"))
    result = store.search("a", "Python")
    assert len(result) == 1
    assert result[0].scope_id == "a"


def test_conversation_response_uses_only_active_scope_memory():
    store = InMemoryMemoryStore()
    store.add(MemoryEntry("a", ConversationScope.PRIVATE, MemoryKind.CONTEXT, "likes Python"))
    store.add(MemoryEntry("b", ConversationScope.PRIVATE, MemoryKind.CONTEXT, "likes Python"))
    engine = ConversationEngine(store)
    message = ConversationMessage("a", ConversationScope.PRIVATE, "user", "Python")
    response = engine.respond(message, lambda text, context, memory: f"seen={len(memory)}")
    assert response.text == "seen=1"
    assert all(item.scope_id == "a" for item in response.memory)


def test_sqlite_memory_persists_and_isolates_scope(tmp_path):
    path = str(tmp_path / "memory.db")
    store = SQLiteMemoryStore(path)
    entry = MemoryEntry("owner", ConversationScope.OWNER, MemoryKind.PREFERENCE, "prefers concise replies")
    store.add(entry)
    store.close()
    reopened = SQLiteMemoryStore(path)
    loaded = reopened.get(entry.memory_id)
    assert loaded == entry
    assert len(reopened.search("owner", "concise")) == 1
    assert reopened.search("other", "concise") == ()
    reopened.close()


def test_invalid_memory_confidence_is_rejected():
    with pytest.raises(ValueError):
        MemoryEntry("a", ConversationScope.PRIVATE, MemoryKind.FACT, "x", confidence=1.1)


def test_policy_rejects_authority_and_oversized_memory():
    policy = MemoryPolicy(max_content_chars=5)
    with pytest.raises(ValueError):
        policy.validate_write(MemoryEntry("a", ConversationScope.PRIVATE, MemoryKind.FACT, "too long"))
    with pytest.raises(PermissionError):
        policy.validate_write(MemoryEntry("a", ConversationScope.PRIVATE, MemoryKind.FACT, "ok", metadata={"authority": "true"}))


def test_decision_memory_requires_explicit_policy():
    entry = MemoryEntry("a", ConversationScope.PRIVATE, MemoryKind.DECISION, "do this")
    with pytest.raises(PermissionError):
        MemoryPolicy().validate_write(entry)
    MemoryPolicy(allow_decisions=True).validate_write(entry)


def test_service_audits_success_and_failure_without_authority_bypass():
    events, audit = EventBus(), AuditLog()
    service = ConversationService(events=events, audit=audit)
    service.remember(MemoryEntry("a", ConversationScope.PRIVATE, MemoryKind.FACT, "likes Python"))
    response = service.receive(ConversationMessage("a", ConversationScope.PRIVATE, "u", "Python"), lambda *_: "hello")
    assert response.text == "hello"
    assert [e.name for e in events.history()] == ["memory.written", "conversation.responded"]
    with pytest.raises(RuntimeError):
        service.receive(ConversationMessage("a", ConversationScope.PRIVATE, "u", "fail"), lambda *_: (_ for _ in ()).throw(RuntimeError()))
    assert audit.history()[-1].event == "conversation.failed"
    assert audit.history()[-1].success is False


def test_message_requires_timezone_aware_timestamp():
    with pytest.raises(ValueError):
        ConversationMessage("a", ConversationScope.PRIVATE, "u", "x", created_at=datetime.now())
