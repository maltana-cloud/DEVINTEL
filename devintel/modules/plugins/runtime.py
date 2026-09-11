"""Minimal execution boundary for specialist engines.

The runtime deliberately does not execute arbitrary plugin source. A plugin supplies a
callable implementation through the host application, while this layer controls
registration, state, scope, permissions, and failure isolation.
"""
from __future__ import annotations
from typing import Callable, Any
from .contracts import PluginAction, PluginResult, PluginState
from .policy import PluginPolicy
from .registry import PluginRegistry

class PluginRuntime:
    def __init__(self, registry: PluginRegistry, policy: PluginPolicy | None = None) -> None:
        self.registry=registry; self.policy=policy or PluginPolicy(); self._handlers: dict[str, Callable[[PluginAction], Any]] = {}
    def attach(self, plugin_id: str, handler: Callable[[PluginAction], Any]) -> None:
        if self.registry.get(plugin_id) is None: raise KeyError(plugin_id)
        self._handlers[plugin_id]=handler
        self.registry.set_state(plugin_id, PluginState.ENABLED)
    def disable(self, plugin_id: str) -> None:
        self._handlers.pop(plugin_id, None); self.registry.set_state(plugin_id, PluginState.DISABLED)
    def isolate(self, plugin_id: str, reason: str) -> None:
        self._handlers.pop(plugin_id, None); self.registry.set_state(plugin_id, PluginState.ISOLATED, reason)
    def execute(self, action: PluginAction, approved: bool = False) -> PluginResult:
        record=self.registry.get(action.plugin_id)
        if record is None: return PluginResult(action.plugin_id, False, error="plugin not registered")
        if record.state != PluginState.ENABLED: return PluginResult(action.plugin_id, False, error=f"plugin not enabled: {record.state.value}")
        if not self.policy.authorize(action, approved): return PluginResult(action.plugin_id, False, error="plugin action denied")
        handler=self._handlers.get(action.plugin_id)
        if handler is None: return PluginResult(action.plugin_id, False, error="plugin handler unavailable")
        try: return PluginResult(action.plugin_id, True, output=handler(action))
        except Exception as exc:
            self.isolate(action.plugin_id, f"execution failure: {type(exc).__name__}")
            return PluginResult(action.plugin_id, False, error="plugin isolated after execution failure")
