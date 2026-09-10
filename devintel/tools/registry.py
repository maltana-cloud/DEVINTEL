"""Versioned registry for external capabilities.

The registry intentionally stores metadata only. Secrets and credentials must
never be committed here; deployment configuration should provide them.
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class ToolSpec:
    name: str
    description: str
    version: str = "1.0"
    status: str = "planned"
    free: bool | None = None
    permissions: tuple[str, ...] = ()
    limits: dict[str, Any] = field(default_factory=dict)


class ToolRegistry:
    def __init__(self) -> None:
        self._tools: dict[str, ToolSpec] = {}

    def register(self, spec: ToolSpec) -> None:
        self._tools[spec.name] = spec

    def get(self, name: str) -> ToolSpec | None:
        return self._tools.get(name)

    def all(self) -> tuple[ToolSpec, ...]:
        return tuple(self._tools.values())
