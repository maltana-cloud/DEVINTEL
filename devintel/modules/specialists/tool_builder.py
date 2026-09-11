"""Tool-building specialist behind the plugin boundary."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Protocol, Sequence
from ..plugins.contracts import PluginAction, PluginManifest, PluginRisk
from ..plugins.service import PluginService
from ..tool_builder.contracts import BuildRequest, ToolRequest, ToolSpec, ToolArtifact, SandboxResult, DeploymentResult
from ..tool_builder.service import ToolBuilderService

@dataclass(frozen=True)
class ToolBuilderSpecialistResult:
    scope_id: str
    artifacts: tuple[tuple[ToolArtifact, SandboxResult, DeploymentResult | None], ...]

class ToolSource(Protocol):
    def discover_tools(self, problem: str) -> Sequence[BuildRequest]: ...

class ToolBuilderSpecialist:
    plugin_id = "specialist.tool_builder"
    def __init__(self, plugins: PluginService | None = None, service: ToolBuilderService | None = None) -> None:
        self.plugins = plugins or PluginService()
        self.service = service or ToolBuilderService()
        self.plugins.register(PluginManifest(self.plugin_id, "Tool Builder Specialist", "1.0.0", "Finds or builds bounded tools through the existing sandbox and permission boundary.", ("tool.discover", "tool.build", "tool.test"), ("tool_builder.read",), PluginRisk.LOW))
        self.attach()
    def attach(self) -> None:
        def run(action: PluginAction) -> ToolBuilderSpecialistResult:
            payload = action.payload
            if not isinstance(payload, dict): raise TypeError("tool-builder action payload must be a mapping")
            source, problem = payload.get("source"), payload.get("problem")
            if not hasattr(source, "discover_tools"): raise TypeError("tool source is invalid")
            if not isinstance(problem, str) or not problem.strip(): raise ValueError("tool problem is required")
            requests = tuple(source.discover_tools(problem.strip()))
            if not all(isinstance(item, BuildRequest) for item in requests): raise TypeError("tool source returned invalid build request")
            results = []
            for request in requests:
                if request.spec.risk != "low":
                    continue
                results.append(self.service.build(request, deploy=False))
            return ToolBuilderSpecialistResult(action.scope_id, tuple(results))
        self.plugins.attach(self.plugin_id, run)
    def execute(self, scope_id: str, problem: str, source: ToolSource) -> ToolBuilderSpecialistResult:
        scope = scope_id.strip() if isinstance(scope_id, str) else ""
        need = problem.strip() if isinstance(problem, str) else ""
        if not scope: raise ValueError("scope_id is required")
        if not need: raise ValueError("problem is required")
        if not hasattr(source, "discover_tools"): raise TypeError("source must implement discover_tools")
        result = self.plugins.execute(PluginAction(self.plugin_id, "tool.build", scope, PluginRisk.LOW, "bounded tool discovery and build", payload={"problem": need, "source": source}))
        if not result.success: raise RuntimeError(result.error)
        return result.output
