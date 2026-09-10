"""Structured audit records for the core execution boundary."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from threading import RLock
from typing import Any


@dataclass(frozen=True)
class AuditRecord:
    event: str
    action: str = ""
    success: bool | None = None
    details: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class AuditLog:
    """Bounded, thread-safe audit trail for decisions and execution outcomes."""

    def __init__(self, history_limit: int = 2000) -> None:
        if history_limit < 1:
            raise ValueError("history_limit must be positive")
        self._records: list[AuditRecord] = []
        self._limit = history_limit
        self._lock = RLock()

    def record(self, entry: AuditRecord) -> AuditRecord:
        with self._lock:
            self._records.append(entry)
            if len(self._records) > self._limit:
                del self._records[: len(self._records) - self._limit]
        return entry

    def history(self) -> tuple[AuditRecord, ...]:
        with self._lock:
            return tuple(self._records)
