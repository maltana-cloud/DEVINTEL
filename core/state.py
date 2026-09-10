"""Explicit runtime state for the DEVINTEL core."""

from __future__ import annotations

from dataclasses import dataclass, field
from threading import RLock
from typing import Any

from .contracts import SecurityState


@dataclass
class RuntimeState:
    security: SecurityState = SecurityState.NORMAL
    running: bool = False
    cycle: int = 0
    last_action: str | None = None
    values: dict[str, Any] = field(default_factory=dict)


class StateStore:
    """Thread-safe state container; no hidden global mutable state."""

    def __init__(self) -> None:
        self._state = RuntimeState()
        self._lock = RLock()

    def snapshot(self) -> RuntimeState:
        with self._lock:
            return RuntimeState(
                security=self._state.security,
                running=self._state.running,
                cycle=self._state.cycle,
                last_action=self._state.last_action,
                values=dict(self._state.values),
            )

    def set_security(self, state: SecurityState) -> None:
        with self._lock:
            self._state.security = state

    def begin_cycle(self) -> int:
        with self._lock:
            self._state.cycle += 1
            self._state.running = True
            return self._state.cycle

    def end_cycle(self, action: str | None = None) -> None:
        with self._lock:
            self._state.running = False
            self._state.last_action = action
