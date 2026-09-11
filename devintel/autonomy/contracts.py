"""Contracts for DEVINTEL's bounded autonomous operating loop."""
from __future__ import annotations
from dataclasses import dataclass, field
from enum import StrEnum
from datetime import datetime, timezone
from typing import Any

class AutonomyPhase(StrEnum):
    OBSERVE="observe"
    UNDERSTAND="understand"
    PLAN="plan"
    PERMISSION="permission"
    ACT="act"
    VERIFY="verify"
    RECORD="record"

@dataclass(frozen=True)
class Observation:
    scope_id: str
    kind: str
    data: Any = None
    observed_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    def __post_init__(self):
        if not self.scope_id.strip() or not self.kind.strip(): raise ValueError("scope_id and kind are required")
        if self.observed_at.tzinfo is None: raise ValueError("observed_at must be timezone-aware")

@dataclass(frozen=True)
class AutonomousCycle:
    cycle_id: str
    scope_id: str
    completed_phases: tuple[AutonomyPhase, ...]
    actions_planned: int
    actions_succeeded: int
    actions_failed: int
    verified: bool
    stopped: bool = False
    stop_reason: str = ""
