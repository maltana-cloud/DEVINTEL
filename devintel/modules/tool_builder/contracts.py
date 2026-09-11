"""Stable contracts for System 6. External code is data, never authority."""
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import StrEnum
from typing import Any

class ToolState(StrEnum):
    DISCOVERED="discovered"; SPECIFIED="specified"; BUILDING="building"; TESTING="testing"; READY="ready"; DEPLOYED="deployed"; FAILED="failed"; ROLLED_BACK="rolled_back"

@dataclass(frozen=True)
class ToolSpec:
    name: str
    description: str
    version: str="0.1.0"
    capabilities: tuple[str,...]=()
    risk: str="low"
    metadata: dict[str,Any]=field(default_factory=dict)
    def __post_init__(self):
        if not self.name.strip() or not self.description.strip(): raise ValueError("tool name and description are required")
        if not self.version.strip(): raise ValueError("version is required")
        if self.risk not in {"low","medium","high","critical"}: raise ValueError("invalid risk")

@dataclass(frozen=True)
class ToolRequest:
    problem: str
    requester: str="system"
    context: dict[str,Any]=field(default_factory=dict)
    def __post_init__(self):
        if not self.problem.strip(): raise ValueError("problem is required")

@dataclass(frozen=True)
class BuildRequest:
    spec: ToolSpec
    source: str
    entrypoint: str=""
    def __post_init__(self):
        if not self.source.strip(): raise ValueError("source is required")

@dataclass(frozen=True)
class ToolArtifact:
    tool: ToolSpec
    source_digest: str
    source: str
    created_at: datetime=field(default_factory=lambda: datetime.now(timezone.utc))

@dataclass(frozen=True)
class SandboxResult:
    success: bool
    output: str=""
    error: str=""
    timed_out: bool=False
    exit_code: int|None=None

@dataclass(frozen=True)
class DeploymentResult:
    success: bool
    tool_name: str
    version: str
    message: str=""
