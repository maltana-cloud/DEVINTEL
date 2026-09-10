"""SQLite persistence for research documents and observations.

The implementation uses only Python's standard library and keeps the same
core behavior as the in-memory store: canonical URL keys and content-hash
deduplication. SQLite is a replaceable backend, not a hard architectural
coupling to the research pipeline.
"""

from __future__ import annotations

import sqlite3
from threading import RLock

from .contracts import ResearchDocument, ResearchObservation, canonicalize_url


class SQLiteResearchStore:
    """Thread-safe SQLite-backed research store."""

    def __init__(self, path: str = ":memory:") -> None:
        if not isinstance(path, str) or not path.strip():
            raise ValueError("database path is required")
        self._connection = sqlite3.connect(path, check_same_thread=False)
        self._connection.row_factory = sqlite3.Row
        self._lock = RLock()
        self._initialize()

    def _initialize(self) -> None:
        with self._lock, self._connection:
            self._connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS research_documents (
                    url TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    content TEXT NOT NULL,
                    publisher TEXT NOT NULL DEFAULT '',
                    published_at TEXT,
                    retrieved_at TEXT NOT NULL,
                    content_hash TEXT NOT NULL UNIQUE,
                    metadata TEXT NOT NULL DEFAULT '{}'
                );
                CREATE TABLE IF NOT EXISTS research_observations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    document_url TEXT NOT NULL,
                    kind TEXT NOT NULL,
                    value TEXT NOT NULL,
                    confidence REAL NOT NULL,
                    evidence TEXT NOT NULL DEFAULT '[]',
                    metadata TEXT NOT NULL DEFAULT '{}'
                );
                CREATE INDEX IF NOT EXISTS idx_observations_document_url
                    ON research_observations(document_url);
                """
            )

    @staticmethod
    def _metadata(value: dict) -> str:
        import json
        return json.dumps(value, sort_keys=True, separators=(",", ":"))

    @staticmethod
    def _parse_metadata(value: str) -> dict:
        import json
        return dict(json.loads(value))

    @staticmethod
    def _document(row: sqlite3.Row) -> ResearchDocument:
        return ResearchDocument(
            row["url"], row["title"], row["content"],
            publisher=row["publisher"],
            published_at=_parse_datetime(row["published_at"]),
            retrieved_at=_parse_datetime(row["retrieved_at"]),
            metadata=SQLiteResearchStore._parse_metadata(row["metadata"]),
        )

    def add_document(self, document: ResearchDocument) -> bool:
        with self._lock, self._connection:
            try:
                self._connection.execute(
                    """INSERT INTO research_documents
                    (url, title, content, publisher, published_at, retrieved_at, content_hash, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                    (
                        canonicalize_url(document.url), document.title, document.content,
                        document.publisher, _format_datetime(document.published_at),
                        _format_datetime(document.retrieved_at), document.content_hash,
                        self._metadata(document.metadata),
                    ),
                )
            except sqlite3.IntegrityError:
                return False
            return True

    def get(self, url: str) -> ResearchDocument | None:
        with self._lock:
            row = self._connection.execute(
                "SELECT * FROM research_documents WHERE url = ?",
                (canonicalize_url(url),),
            ).fetchone()
            return None if row is None else self._document(row)

    def add_observation(self, observation: ResearchObservation) -> None:
        import json
        with self._lock, self._connection:
            self._connection.execute(
                """INSERT INTO research_observations
                (document_url, kind, value, confidence, evidence, metadata)
                VALUES (?, ?, ?, ?, ?, ?)""",
                (
                    canonicalize_url(observation.document_url), observation.kind,
                    observation.value, observation.confidence,
                    json.dumps(list(observation.evidence), ensure_ascii=False),
                    self._metadata(observation.metadata),
                ),
            )

    def documents(self) -> tuple[ResearchDocument, ...]:
        with self._lock:
            rows = self._connection.execute(
                "SELECT * FROM research_documents ORDER BY rowid"
            ).fetchall()
            return tuple(self._document(row) for row in rows)

    def observations(self) -> tuple[ResearchObservation, ...]:
        import json
        with self._lock:
            rows = self._connection.execute(
                "SELECT * FROM research_observations ORDER BY id"
            ).fetchall()
            return tuple(
                ResearchObservation(
                    row["document_url"], row["kind"], row["value"],
                    confidence=row["confidence"],
                    evidence=tuple(json.loads(row["evidence"])),
                    metadata=self._parse_metadata(row["metadata"]),
                )
                for row in rows
            )

    def count_documents(self) -> int:
        with self._lock:
            return int(self._connection.execute("SELECT COUNT(*) FROM research_documents").fetchone()[0])

    def count_observations(self) -> int:
        with self._lock:
            return int(self._connection.execute("SELECT COUNT(*) FROM research_observations").fetchone()[0])

    def close(self) -> None:
        with self._lock:
            self._connection.close()


def _format_datetime(value) -> str | None:
    return None if value is None else value.isoformat()


def _parse_datetime(value):
    if value is None:
        return None
    from datetime import datetime
    return datetime.fromisoformat(value)
