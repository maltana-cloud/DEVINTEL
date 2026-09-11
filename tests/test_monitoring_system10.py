from devintel.modules.monitoring import (
    AlertSeverity, HealthCheck, HealthState, InMemoryMonitoringStore,
    MonitoringEngine, QueueSnapshot,
)


def test_report_and_overall_state_are_scope_isolated():
    engine = MonitoringEngine(InMemoryMonitoringStore())
    engine.record_health(HealthCheck("core", "a", HealthState.HEALTHY))
    engine.record_health(HealthCheck("worker", "a", HealthState.DEGRADED))
    engine.record_health(HealthCheck("core", "b", HealthState.FAILED))
    engine.record_queue(QueueSnapshot("work", "a", pending=3))
    engine.alert("a", AlertSeverity.WARNING, "queue", "backlog", "a1")

    assert engine.overall_state("a") == HealthState.DEGRADED
    assert engine.overall_state("b") == HealthState.FAILED
    report = engine.report("a", security_events=2, errors=1, revenue_records=4)
    assert len(report.health) == 2
    assert len(report.queues) == 1
    assert len(report.alerts) == 1
    assert report.security_events == 2
    assert engine.report("b").queues == ()


def test_failed_state_has_priority():
    engine = MonitoringEngine(InMemoryMonitoringStore())
    engine.record_health(HealthCheck("x", "scope", HealthState.HEALTHY))
    engine.record_health(HealthCheck("y", "scope", HealthState.FAILED))
    assert engine.overall_state("scope") == HealthState.FAILED


def test_invalid_metrics_are_rejected():
    engine = MonitoringEngine(InMemoryMonitoringStore())
    try:
        engine.report("scope", errors=-1)
    except ValueError:
        pass
    else:
        raise AssertionError("negative metrics must fail closed")
