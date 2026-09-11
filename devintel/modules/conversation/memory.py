"""Memory storage with strict scope isolation and relevance retrieval."""

from __future__ import annotations

from threading import RLock
from typing import Protocol

from .contracts import MemoryEntry


class MemoryStore(Protocol):
    def add(self, entry: MemoryEntry) -> MemoryEntry: ...
    def get(self, memory_id: str) -> MemoryEntry | None: ...
    def search(self, scope_id: str, query: str, limit: int = 10) -> tuple[MemoryEntry, ...]: ...
    def list_scope(self, scope_id: str, limit: int = 100) -> tuple[MemoryEntry, ...]: ...


class InMemoryMemoryStore:
    """Thread-safe bounded memory store; retrieval can never cross scope_id."""

    def __init__(self, max_entries: int = 10_000) -> None:
        if max_entries < 1:
            raise ValueError("max_entries must be positive")
        self._max_entries = max_entries
        self._items: dict[str, MemoryEntry] = {}
        self._lock = RLock()

    def add(self, entry: MemoryEntry) -> MemoryEntry:
        with self._lock:
            if entry.memory_id not in self._items and len(self._items) >= self._max_entries:
                oldest = min(self._items.values(), key=lambda item: item.created_at)
                self._items.pop(oldest.memory_id, None)
            self._items[entry.memory_id] = entry
            return entry

    def get(self, memory_id: str) -> MemoryEntry | None:
        with self._lock:
            return self._items.get(memory_id)

    def list_scope(self, scope_id: str, limit: int = 100) -> tuple[MemoryEntry, ...]:
        if not scope_id.strip() or limit < 1:
            raise ValueError("scope_id and positive limit are required")
        with self._lock:
            items = [item for item in self._items.values() if item.scope_id == scope_id]
            items.sort(key=lambda item: item.created_at, reverse=True)
            return tuple(items[:limit])

    def search(self, scope_id: str, query: str, limit: int = 10) -> tuple[MemoryEntry, ...]:
        if not scope_id.strip() or not query.strip() or limit < 1:
            raise ValueError("scope_id, query, and positive limit are required")
        tokens = {token.lower() for token in query.split() if token.strip()}
        with self._lock:
            scored: list[tuple[int, MemoryEntry]] = []
            for item in self._items.values():
                if item.scope_id != scope_id:
                    continue
                words = set(item.content.lower().split())
                score = len(tokens & words)
                if score:
                    scored.append((score, item))
            scored.sort(key=lambda pair: (pair[0], pair[1].created_at), reverse=True)
            return tuple(item for _, item in scored[:limit])
