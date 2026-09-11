"""Monitoring and owner-control intelligence specialist."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Protocol, Sequence
from ..monitoring.contracts import HealthCheck, QueueSnapshot, OwnerReport, AlertSeverity
from ..monitoring.engine import MonitoringEngine
from ..plugins.contracts import PluginAction, PluginManifest, PluginRisk
from ..plugins.service import PluginService

@dataclass(frozen=True)
class MonitoringSpecialistResult:
    scope_id: str
    report: OwnerReport

class MonitoringSource(Protocol):
    def health_checks(self, scope_id: str) -> Sequence[HealthCheck]: ...
    def queues(self, scope_id: str) -> Sequence[QueueSnapshot]: ...

class MonitoringSpecialist:
    plugin_id = "specialist.monitoring"
    def __init__(self, plugins: PluginService | None = None, engine: MonitoringEngine | None = None) -> None:
        self.plugins = plugins or PluginService()
        self.engine = engine or MonitoringEngine()
        self.plugins.register(PluginManifest(self.plugin_id, "Monitoring Specialist", "1.0.0", "Builds scoped operational reports and alerts without granting authority.", ("monitoring.observe", "monitoring.report"), ("monitoring.read",), PluginRisk.LOW))
        self.attach()
    def attach(self) -> None:
        def run(action: PluginAction) -> MonitoringSpecialistResult:
            payload = action.payload
            if not isinstance(payload, dict): raise TypeError("monitoring action payload must be a mapping")
            source, scope = payload.get("source"), action.scope_id
            if not hasattr(source, "health_checks") or not hasattr(source, "queues"): raise TypeError("monitoring source is invalid")
            for check in source.health_checks(scope):
                self.engine.record_health(check)
            for queue in source.queues(scope):
                self.engine.record_queue(queue)
            return MonitoringSpecialistResult(scope, self.engine.report(scope))
        self.plugins.attach(self.plugin_id, run)
    def execute(self, scope_id: str, source: MonitoringSource) -> MonitoringSpecialistResult:
        scope = scope_id.strip() if isinstance(scope_id, str) else ""
        if not scope: raise ValueError("scope_id is required")
        if not hasattr(source, "health_checks") or not hasattr(source, "queues"): raise TypeError("source must implement health_checks and queues")
        result = self.plugins.execute(PluginAction(self.plugin_id, "monitoring.scan", scope, PluginRisk.LOW, "bounded monitoring observation", payload={"source": source}))
        if not result.success: raise RuntimeError(result.error)
        return result.output
