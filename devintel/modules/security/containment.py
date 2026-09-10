"""Scoped containment and recovery primitives."""

from __future__ import annotations

from dataclasses import dataclass
from threading import RLock

from .contracts import ContainmentRecord, RecoveryRecord, SecurityState


@dataclass
class _Scope:
    state: SecurityState = SecurityState.NORMAL
    capabilities: set[str] = None

    def __post_init__(self) -> None:
        if self.capabilities is None:
            self.capabilities = set()


class ContainmentManager:
    """Isolate only the affected scope; unrelated scopes remain untouched."""

    def __init__(self) -> None:
        self._lock = RLock()
        self._scopes: dict[str, _Scope] = {}

    def register(self, scope: str, capabilities: set[str] | None = None) -> None:
        if not scope.strip():
            raise ValueError("scope is required")
        with self._lock:
            self._scopes.setdefault(scope, _Scope(capabilities=set(capabilities or ())))

    def state(self, scope: str) -> SecurityState:
        with self._lock:
            return self._scopes.get(scope, _Scope()).state

    def capabilities(self, scope: str) -> frozenset[str]:
        with self._lock:
            return frozenset(self._scopes.get(scope, _Scope()).capabilities)

    def contain(self, scope: str, reason: str) -> ContainmentRecord:
        if not reason.strip():
            raise ValueError("containment reason is required")
        with self._lock:
            item = self._scopes.setdefault(scope, _Scope())
            previous = item.state
            revoked = tuple(sorted(item.capabilities))
            item.capabilities.clear()
            item.state = SecurityState.CONTAINMENT
            return ContainmentRecord(scope, previous, item.state, revoked, reason, False)

    def begin_recovery(self, scope: str) -> RecoveryRecord:
        with self._lock:
            item = self._scopes.setdefault(scope, _Scope())
            item.state = SecurityState.RECOVERY
            return RecoveryRecord(scope, item.state, False, (), "recovery started")

    def restore(self, scope: str, checks: tuple[str, ...]) -> RecoveryRecord:
        if not checks or any(not check.strip() for check in checks):
            raise ValueError("recovery requires non-empty verification checks")
        with self._lock:
            item = self._scopes.setdefault(scope, _Scope())
            if item.state != SecurityState.RECOVERY:
                raise RuntimeError("scope must be in recovery before restoration")
            item.state = SecurityState.RESTORED
            return RecoveryRecord(scope, item.state, True, checks, "restoration verified")

    def safe_degraded(self, scope: str, reason: str) -> RecoveryRecord:
        if not reason.strip():
            raise ValueError("reason is required")
        with self._lock:
            item = self._scopes.setdefault(scope, _Scope())
            item.state = SecurityState.SAFE_DEGRADED
            item.capabilities.clear()
            return RecoveryRecord(scope, item.state, True, ("capabilities revoked",), reason)
