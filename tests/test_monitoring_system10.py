from datetime import datetime, timezone
from devintel.modules.monitoring import AlertSeverity, HealthCheck, HealthState, InMemoryMonitoringStore, MonitoringEngine, QueueSnapshot

def test_health_and_report_are_scope_isolated():
    e = MonitoringEngine(InMemoryMonitoringStore())
    e.record_health(HealthCheck("core", "a", HealthState.HEALTHY, observed_at=datetime.now(timezone.utc)))
    e.record_health(HealthCheck("core", "b", HealthState.FAILED, observed_at=datetime.now(timezone.utc)))
    e.record_queue(QueueSnapshot("work", "a", pending=2))
    assert e.overall_state("a") == HealthState.HEALTHY
    assert e.overall_state("b") == HealthState.FAILED
    assert len(e.report("a").queues) == 1
    assert not e.report("b").queues

def test_alerts_are_scoped():
    e = MonitoringEngine()
    e.alert("a", AlertSeverity.WARNING, "queue", "backlog")
    assert len(e.report("a").alerts) == 1
    assert not e.report("b").alerts

def test_monitoring_does_not_grant_authority():
    e = MonitoringEngine()
    report = e.report("owner")
    assert report.scope_id == "owner"
    assert e.overall_state("owner") == HealthState.UNKNOWN
