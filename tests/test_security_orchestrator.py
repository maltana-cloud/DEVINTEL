from devintel.core.audit import AuditLog
from devintel.core.events import EventBus
from devintel.core.state import RuntimeState, StateStore
from devintel.modules.security import SecurityEvent, SecurityOrchestrator, SecurityState, ThreatLevel


def test_orchestrator_contains_high_risk_scope_and_records_audit():
    audit = AuditLog()
    events = EventBus()
    manager = SecurityOrchestrator(audit=audit, events=events)
    manager.containment.register("channel:a", {"publish", "read"})
    manager.containment.register("channel:b", {"publish"})

    result = manager.detect(SecurityEvent("prompt_injection", ThreatLevel.HIGH, "channel:a", "untrusted instruction"))

    assert result.state == SecurityState.CONTAINMENT
    assert result.capabilities_revoked == ("publish", "read")
    assert manager.containment.state("channel:b") == SecurityState.NORMAL
    assert "security.detected" in [item.name for item in events.history()]
    assert any(item.event == "security.contained" for item in audit.history())


def test_critical_detection_syncs_core_state_but_does_not_need_core_authority():
    state = StateStore()
    orchestrator = SecurityOrchestrator(runtime_state=state)

    result = orchestrator.detect(SecurityEvent("credential_anomaly", ThreatLevel.CRITICAL, "provider:x", "unexpected use"))

    assert result.state == SecurityState.CONTAINMENT
    assert state.state == RuntimeState.CONTAINMENT


def test_recovery_and_restore_emit_auditable_events():
    audit = AuditLog()
    events = EventBus()
    orchestrator = SecurityOrchestrator(audit=audit, events=events)
    orchestrator.detect(SecurityEvent("incident", ThreatLevel.HIGH, "channel:a", "incident"))
    orchestrator.begin_recovery("channel:a")
    record = orchestrator.restore("channel:a", ("credential revoked", "health check passed"))

    assert record.verified
    names = [event.name for event in events.history()]
    assert names[-2:] == ["security.recovery_started", "security.restored"]
    assert len(orchestrator.owner_summary()) >= 3


def test_safe_degraded_path_revokes_scope_capabilities():
    orchestrator = SecurityOrchestrator()
    orchestrator.containment.register("research", {"fetch", "store"})
    record = orchestrator.safe_degraded("research", "provider outage")

    assert record.state == SecurityState.SAFE_DEGRADED
    assert orchestrator.containment.capabilities("research") == frozenset()
