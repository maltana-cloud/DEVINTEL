"""High-level plugin lifecycle service."""
from __future__ import annotations
from .contracts import PluginAction, PluginManifest, PluginResult, PluginState
from .registry import PluginRegistry
from .runtime import PluginRuntime

class PluginService:
    def __init__(self, registry: PluginRegistry | None = None, runtime: PluginRuntime | None = None) -> None:
        self.registry=registry or PluginRegistry()
        self.runtime=runtime or PluginRuntime(self.registry)
    def register(self, manifest: PluginManifest): return self.registry.register(manifest)
    def attach(self, plugin_id: str, handler): self.runtime.attach(plugin_id, handler)
    def disable(self, plugin_id: str): self.runtime.disable(plugin_id)
    def isolate(self, plugin_id: str, reason: str): self.runtime.isolate(plugin_id, reason)
    def execute(self, action: PluginAction, approved: bool = False) -> PluginResult: return self.runtime.execute(action, approved)
    def status(self) -> list[tuple[str, PluginState, int]]:
        return [(r.manifest.plugin_id, r.state, r.generation) for r in self.registry.all()]
