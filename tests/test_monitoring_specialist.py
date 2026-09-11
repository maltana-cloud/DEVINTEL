from datetime import datetime, timezone
from devintel.modules.monitoring.contracts import HealthCheck, HealthState, QueueSnapshot
from devintel.modules.specialists.monitoring import MonitoringSpecialist

class Source:
    def health_checks(self, scope_id):
        return [HealthCheck("core", scope_id, HealthState.HEALTHY, "ok", datetime.now(timezone.utc))]
    def queues(self, scope_id):
        return [QueueSnapshot("work", scope_id, 2, 0, 1.0)]

def test_monitoring_specialist_reports_scoped_state():
    result = MonitoringSpecialist().execute("scope", Source())
    assert result.scope_id == "scope"
    assert result.report.scope_id == "scope"
    assert result.report.health[0].state is HealthState.HEALTHY
    assert result.report.queues[0].pending == 2

def test_monitoring_specialist_rejects_invalid_scope():
    try:
        MonitoringSpecialist().execute("", Source())
    except ValueError as exc:
        assert "scope_id" in str(exc)
    else:
        raise AssertionError("expected ValueError")
