"""Security orchestration over the existing core event, state, and audit boundaries."""

from __future__ import annotations

from dataclasses import dataclass
from threading import RLock
from typing import Iterable

from ...core.audit import AuditLog, AuditRecord
from ...core.events import EventBus, RuntimeEvent
from ...core.state import RuntimeState, StateStore
from .containment import ContainmentManager
from .contracts import RecoveryRecord, SecurityEvent, SecurityState, ThreatLevel


_TARGETS = {
    ThreatLevel.LOW: SecurityState.WATCH,
    ThreatLevel.MEDIUM: SecurityState.RESTRICTED,
    ThreatLevel.HIGH: SecurityState.CONTAINMENT,
    ThreatLevel.CRITICAL: SecurityState.CONTAINMENT,
}


@dataclass(frozen=True)
class SecurityAction:
    scope: str
    state: SecurityState
    capabilities_revoked: tuple[str, ...] = ()
    reason: str = ""


class SecurityOrchestrator:
    """Coordinate detection, containment and recovery without granting authority."""

    def __init__(
        self,
        *,
        containment: ContainmentManager | None = None,
        events: EventBus | None = None,
        audit: AuditLog | None = None,
        runtime_state: StateStore | None = None,
    ) -> None:
        self.containment = containment or ContainmentManager()
        self.events = events or EventBus()
        self.audit = audit or AuditLog()
        self.runtime_state = runtime_state
        self._lock = RLock()

    @staticmethod
    def _runtime_state(target: SecurityState) -> RuntimeState:
        return RuntimeState(target.value[3:].lower())

    def detect(self, event: SecurityEvent) -> SecurityAction:
        """Handle a threat using the minimum state required by its level."""
        target = _TARGETS[event.level]
        self.containment.register(event.scope)
        self.events.publish(RuntimeEvent("security.detected", {
            "kind": event.kind,
            "level": event.level.value,
            "scope": event.scope,
            "reason": event.reason,
            "source": event.source,
        }))
        self.audit.record(AuditRecord(
            event="security.detected",
            action=event.kind,
            success=True,
            details={"scope": event.scope, "level": event.level.value},
        ))

        if target == SecurityState.WATCH:
            return SecurityAction(event.scope, self.containment.state(event.scope), reason=event.reason)
        if target == SecurityState.RESTRICTED:
            return self._restrict(event.scope, event.reason)
        return self._contain(event.scope, event.reason)

    def _restrict(self, scope: str, reason: str) -> SecurityAction:
        self.events.publish(RuntimeEvent("security.restricted", {"scope": scope, "reason": reason}))
        self.audit.record(AuditRecord("security.restricted", "restrict", True, {"scope": scope}))
        return SecurityAction(scope, SecurityState.RESTRICTED, reason=reason)

    def _contain(self, scope: str, reason: str) -> SecurityAction:
        record = self.containment.contain(scope, reason)
        # Scoped incidents must remain isolated. Only an explicit core-scoped
        # incident is allowed to change the global runtime state.
        if scope == "core":
            self._sync_runtime(RuntimeState.CONTAINMENT)
        self.events.publish(RuntimeEvent("security.contained", {
            "scope": scope,
            "revoked_capabilities": record.revoked_capabilities,
            "reason": reason,
        }))
        self.audit.record(AuditRecord(
            "security.contained", "contain", True,
            {"scope": scope, "revoked_capabilities": record.revoked_capabilities},
        ))
        return SecurityAction(scope, record.state, record.revoked_capabilities, reason)

    def begin_recovery(self, scope: str) -> RecoveryRecord:
        record = self.containment.begin_recovery(scope)
        if scope == "core":
            self._sync_runtime(RuntimeState.RECOVERY)
        self.events.publish(RuntimeEvent("security.recovery_started", {"scope": scope}))
        self.audit.record(AuditRecord("security.recovery_started", "recover", True, {"scope": scope}))
        return record

    def restore(self, scope: str, checks: Iterable[str]) -> RecoveryRecord:
        checks_tuple = tuple(checks)
        record = self.containment.restore(scope, checks_tuple)
        if not record.verified:
            raise RuntimeError("restoration requires verified recovery")
        if scope == "core":
            self._sync_runtime(RuntimeState.RESTORED)
        self.events.publish(RuntimeEvent("security.restored", {"scope": scope, "checks": checks_tuple}))
        self.audit.record(AuditRecord("security.restored", "restore", True, {"scope": scope, "checks": checks_tuple}))
        return record

    def safe_degraded(self, scope: str, reason: str) -> RecoveryRecord:
        record = self.containment.safe_degraded(scope, reason)
        if scope == "core":
            self._sync_runtime(RuntimeState.SAFE_DEGRADED)
        self.events.publish(RuntimeEvent("security.safe_degraded", {"scope": scope, "reason": reason}))
        self.audit.record(AuditRecord("security.safe_degraded", "degrade", True, {"scope": scope}))
        return record

    def owner_summary(self) -> tuple[AuditRecord, ...]:
        """Return bounded owner-visible security history without exposing secrets."""
        return self.audit.history()

    def _sync_runtime(self, target: RuntimeState) -> None:
        if self.runtime_state is None:
            return
        current = self.runtime_state.state
        if current == target:
            return
        try:
            self.runtime_state.transition(target)
        except Exception:
            # Security must not fail open because the optional core mirror cannot
            # follow a transition. The security subsystem remains authoritative
            # for its own scoped containment decision.
            self.audit.record(AuditRecord(
                "security.runtime_sync_failed", "state_sync", False,
                {"current": current.value, "target": target.value},
            ))
