from devintel.modules.conversation import (
    ConversationEngine, ConversationMessage, ConversationScope, InMemoryMemoryStore,
    MemoryEntry, MemoryKind, SQLiteMemoryStore,
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
    try:
        MemoryEntry("a", ConversationScope.PRIVATE, MemoryKind.FACT, "x", confidence=1.1)
    except ValueError:
        pass
    else:
        raise AssertionError("invalid confidence must fail closed")
