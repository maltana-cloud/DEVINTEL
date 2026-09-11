"""Contracts for the DEVINTEL owner control center."""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum

class ControlDecision(str, Enum):
    ALLOW = "allow"
    DENY = "deny"
    APPROVAL_REQUIRED = "approval_required"

@dataclass(frozen=True)
class ControlCommand:
    command_id: str
    scope_id: str
    action: str
    reason: str = ""
    requested_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    requires_owner_approval: bool = False
    def __post_init__(self) -> None:
        if not self.command_id.strip() or not self.scope_id.strip() or not self.action.strip():
            raise ValueError("command_id, scope_id, and action are required")
        if self.requested_at.tzinfo is None or self.requested_at.utcoffset() is None:
            raise ValueError("requested_at must be timezone-aware")

@dataclass(frozen=True)
class ControlSnapshot:
    scope_id: str
    runtime_state: str
    monitoring_state: str
    plugin_count: int
    audit_events: int
    pending_approvals: int = 0
    def __post_init__(self) -> None:
        if not self.scope_id.strip(): raise ValueError("scope_id is required")
        if min(self.plugin_count, self.audit_events, self.pending_approvals) < 0:
            raise ValueError("snapshot counters cannot be negative")
