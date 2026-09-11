"""Composition root connecting DEVINTEL's bounded subsystems."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from ..control.service import OwnerControlCenter
from ..core.audit import AuditLog
from ..core.orchestrator import Orchestrator
from ..core.runtime import RuntimeContext
from ..modules.monitoring.engine import MonitoringEngine
from ..modules.plugins.service import PluginService
from ..modules.security.orchestrator import SecurityOrchestrator
from ..providers.registry import ProviderRegistry

@dataclass(frozen=True)
class RuntimeSnapshot:
    """Owner-facing operational snapshot; observations never grant authority."""
    scope_id: str
    runtime_state: str
    metrics: dict[str, int]
    plugin_status: tuple[tuple[str, str, int], ...]
    monitoring_state: str
    audit_events: int

class DEVINTELRuntime:
    """Single composition root for DEVINTEL bounded subsystems."""
    def __init__(self) -> None:
        self.context = RuntimeContext()
        self.audit = AuditLog()
        self.orchestrator = Orchestrator(runtime=self.context, audit=self.audit)
        self.security = SecurityOrchestrator(events=self.context.events, audit=self.audit, runtime_state=self.context.state)
        self.monitoring = MonitoringEngine()
        self.plugins = PluginService()
        self.providers = ProviderRegistry()
        self.control = OwnerControlCenter(self)

    def register_action(self, action: str, handler: Any) -> None:
        self.orchestrator.register(action, handler)

    def execute(self, request: Any, *, owner_approved: bool = False, value: float = 0.0):
        return self.orchestrator.execute(request, owner_approved=owner_approved, value=value)

    def snapshot(self, scope_id: str) -> RuntimeSnapshot:
        if not isinstance(scope_id, str) or not scope_id.strip():
            raise ValueError("scope_id is required")
        plugins = tuple((plugin_id, state.value, generation) for plugin_id, state, generation in self.plugins.status())
        return RuntimeSnapshot(scope_id, self.context.state.state.value, self.context.snapshot_metrics(), plugins, self.monitoring.overall_state(scope_id).value, len(self.audit.history()))
