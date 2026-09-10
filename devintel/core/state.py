"""Controlled runtime and security state machine."""

from __future__ import annotations

from enum import StrEnum
from threading import RLock


class RuntimeState(StrEnum):
    NORMAL = "normal"
    WATCH = "watch"
    RESTRICTED = "restricted"
    CONTAINMENT = "containment"
    RECOVERY = "recovery"
    RESTORED = "restored"
    SAFE_DEGRADED = "safe_degraded"


_ALLOWED: dict[RuntimeState, frozenset[RuntimeState]] = {
    RuntimeState.NORMAL: frozenset({RuntimeState.WATCH, RuntimeState.RESTRICTED, RuntimeState.SAFE_DEGRADED}),
    RuntimeState.WATCH: frozenset({RuntimeState.NORMAL, RuntimeState.RESTRICTED, RuntimeState.CONTAINMENT, RuntimeState.SAFE_DEGRADED}),
    RuntimeState.RESTRICTED: frozenset({RuntimeState.NORMAL, RuntimeState.CONTAINMENT, RuntimeState.RECOVERY, RuntimeState.SAFE_DEGRADED}),
    RuntimeState.CONTAINMENT: frozenset({RuntimeState.RECOVERY, RuntimeState.SAFE_DEGRADED}),
    RuntimeState.RECOVERY: frozenset({RuntimeState.RESTORED, RuntimeState.CONTAINMENT, RuntimeState.SAFE_DEGRADED}),
    RuntimeState.RESTORED: frozenset({RuntimeState.NORMAL, RuntimeState.WATCH, RuntimeState.RESTRICTED}),
    RuntimeState.SAFE_DEGRADED: frozenset({RuntimeState.RECOVERY, RuntimeState.NORMAL, RuntimeState.CONTAINMENT}),
}


class InvalidStateTransition(RuntimeError):
    """Raised when a caller attempts an unsafe state transition."""


class StateStore:
    """Thread-safe state store with explicit, fail-closed transitions."""

    def __init__(self, initial: RuntimeState = RuntimeState.NORMAL) -> None:
        self._state = initial
        self._lock = RLock()

    @property
    def state(self) -> RuntimeState:
        with self._lock:
            return self._state

    def transition(self, target: RuntimeState) -> RuntimeState:
        with self._lock:
            if target == self._state:
                return self._state
            if target not in _ALLOWED[self._state]:
                raise InvalidStateTransition(f"{self._state} -> {target} is not allowed")
            self._state = target
            return self._state
