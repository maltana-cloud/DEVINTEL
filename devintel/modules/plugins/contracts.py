"""Contracts for DEVINTEL's provider-independent plugin/engine layer."""
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Mapping

class PluginState(str, Enum):
    DISCOVERED="DISCOVERED"; ENABLED="ENABLED"; DISABLED="DISABLED"; FAILED="FAILED"; ISOLATED="ISOLATED"

class PluginRisk(str, Enum):
    LOW="LOW"; MEDIUM="MEDIUM"; HIGH="HIGH"; CRITICAL="CRITICAL"

@dataclass(frozen=True)
class PluginManifest:
    plugin_id: str
    name: str
    version: str
    description: str
    capabilities: tuple[str, ...] = ()
    required_permissions: tuple[str, ...] = ()
    risk: PluginRisk = PluginRisk.LOW
    metadata: Mapping[str, str] = field(default_factory=dict)
    def __post_init__(self) -> None:
        if not self.plugin_id.strip() or not self.name.strip() or not self.version.strip() or not self.description.strip():
            raise ValueError("plugin id, name, version, and description are required")
        if any(not x.strip() for x in self.capabilities + self.required_permissions):
            raise ValueError("plugin capabilities and permissions must be non-empty")

@dataclass(frozen=True)
class PluginRecord:
    manifest: PluginManifest
    state: PluginState = PluginState.DISCOVERED
    generation: int = 1
    failure_reason: str = ""

@dataclass(frozen=True)
class PluginAction:
    plugin_id: str
    action: str
    scope_id: str
    risk: PluginRisk = PluginRisk.LOW
    reason: str = ""
    requires_owner_approval: bool = False
    payload: object = None

@dataclass(frozen=True)
class PluginResult:
    plugin_id: str
    success: bool
    output: object = None
    error: str = ""
