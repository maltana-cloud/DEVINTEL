"""Optional standard-library SQLite persistence for conversation memory."""

from __future__ import annotations

import json
import sqlite3
from threading import RLock

from .contracts import ConversationScope, MemoryEntry, MemoryKind


class SQLiteMemoryStore:
    """Thread-safe persistent store with scope-isolated queries."""

    def __init__(self, path: str = ":memory:") -> None:
        if not isinstance(path, str) or not path.strip():
            raise ValueError("database path is required")
        self._db = sqlite3.connect(path, check_same_thread=False)
        self._db.row_factory = sqlite3.Row
        self._lock = RLock()
        with self._db:
            self._db.execute(
                """CREATE TABLE IF NOT EXISTS conversation_memory (
                    memory_id TEXT PRIMARY KEY,
                    scope_id TEXT NOT NULL,
                    scope TEXT NOT NULL,
                    kind TEXT NOT NULL,
                    content TEXT NOT NULL,
                    confidence REAL NOT NULL,
                    source_message_id TEXT,
                    created_at TEXT NOT NULL,
                    metadata TEXT NOT NULL
                )"""
            )
            self._db.execute("CREATE INDEX IF NOT EXISTS idx_memory_scope ON conversation_memory(scope_id)")

    @staticmethod
    def _entry(row: sqlite3.Row) -> MemoryEntry:
        from datetime import datetime
        return MemoryEntry(
            scope_id=row["scope_id"],
            scope=ConversationScope(row["scope"]),
            kind=MemoryKind(row["kind"]),
            content=row["content"],
            confidence=row["confidence"],
            source_message_id=row["source_message_id"],
            memory_id=row["memory_id"],
            created_at=datetime.fromisoformat(row["created_at"]),
            metadata=json.loads(row["metadata"]),
        )

    def add(self, entry: MemoryEntry) -> MemoryEntry:
        with self._lock, self._db:
            self._db.execute(
                """INSERT OR REPLACE INTO conversation_memory
                (memory_id, scope_id, scope, kind, content, confidence, source_message_id, created_at, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (entry.memory_id, entry.scope_id, entry.scope.value, entry.kind.value,
                 entry.content, entry.confidence, entry.source_message_id,
                 entry.created_at.isoformat(), json.dumps(dict(entry.metadata), sort_keys=True)),
            )
        return entry

    def get(self, memory_id: str) -> MemoryEntry | None:
        with self._lock:
            row = self._db.execute("SELECT * FROM conversation_memory WHERE memory_id=?", (memory_id,)).fetchone()
            return None if row is None else self._entry(row)

    def list_scope(self, scope_id: str, limit: int = 100) -> tuple[MemoryEntry, ...]:
        if not scope_id.strip() or limit < 1:
            raise ValueError("scope_id and positive limit are required")
        with self._lock:
            rows = self._db.execute(
                "SELECT * FROM conversation_memory WHERE scope_id=? ORDER BY created_at DESC LIMIT ?",
                (scope_id, limit),
            ).fetchall()
            return tuple(self._entry(row) for row in rows)

    def search(self, scope_id: str, query: str, limit: int = 10) -> tuple[MemoryEntry, ...]:
        if not scope_id.strip() or not query.strip() or limit < 1:
            raise ValueError("scope_id, query, and positive limit are required")
        tokens = [token.lower() for token in query.split() if token.strip()]
        clauses = " OR ".join("LOWER(content) LIKE ?" for _ in tokens)
        params = [scope_id, *[f"%{token}%" for token in tokens], limit]
        with self._lock:
            rows = self._db.execute(
                f"SELECT * FROM conversation_memory WHERE scope_id=? AND ({clauses}) ORDER BY created_at DESC LIMIT ?",
                params,
            ).fetchall()
            return tuple(self._entry(row) for row in rows)

    def close(self) -> None:
        with self._lock:
            self._db.close()
