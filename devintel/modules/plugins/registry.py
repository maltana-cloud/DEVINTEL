"""Thread-safe registry with per-plugin lifecycle isolation."""
from __future__ import annotations
from threading import RLock
from .contracts import PluginManifest, PluginRecord, PluginState

class PluginRegistry:
    def __init__(self, max_plugins: int = 1024) -> None:
        if max_plugins < 1: raise ValueError("max_plugins must be positive")
        self._max = max_plugins; self._items: dict[str, PluginRecord] = {}; self._lock = RLock()
    def register(self, manifest: PluginManifest) -> PluginRecord:
        with self._lock:
            old = self._items.get(manifest.plugin_id)
            if old is not None and old.manifest.version == manifest.version: return old
            if old is None and len(self._items) >= self._max: raise RuntimeError("plugin registry capacity reached")
            generation = 1 if old is None else old.generation + 1
            record = PluginRecord(manifest, PluginState.DISCOVERED, generation)
            self._items[manifest.plugin_id] = record
            return record
    def get(self, plugin_id: str) -> PluginRecord | None:
        with self._lock: return self._items.get(plugin_id)
    def all(self) -> list[PluginRecord]:
        with self._lock: return list(self._items.values())
    def set_state(self, plugin_id: str, state: PluginState, reason: str = "") -> PluginRecord:
        with self._lock:
            current = self._items.get(plugin_id)
            if current is None: raise KeyError(plugin_id)
            updated = PluginRecord(current.manifest, state, current.generation, reason)
            self._items[plugin_id] = updated
            return updated
