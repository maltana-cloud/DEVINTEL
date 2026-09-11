"""Owner-facing control center with fail-closed command handling."""
from __future__ import annotations
from uuid import uuid4
from typing import Any
from .contracts import ControlCommand, ControlDecision, ControlSnapshot

class OwnerControlCenter:
    """Read operational state and gate sensitive commands; never bypasses core policy."""
    def __init__(self, runtime: Any) -> None:
        self.runtime = runtime
        self._pending: dict[str, ControlCommand] = {}

    def snapshot(self, scope_id: str) -> ControlSnapshot:
        snap = self.runtime.snapshot(scope_id)
        return ControlSnapshot(
            scope_id=scope_id,
            runtime_state=snap.runtime_state,
            monitoring_state=snap.monitoring_state,
            plugin_count=len(snap.plugin_status),
            audit_events=snap.audit_events,
            pending_approvals=len(self._pending),
        )

    def request(self, scope_id: str, action: str, *, reason: str = "", requires_owner_approval: bool = True) -> ControlCommand:
        command = ControlCommand(uuid4().hex, scope_id, action, reason, requires_owner_approval=requires_owner_approval)
        self._pending[command.command_id] = command
        return command

    def decide(self, command: ControlCommand, *, owner_approved: bool = False) -> ControlDecision:
        if command.command_id not in self._pending:
            return ControlDecision.DENY
        if command.requires_owner_approval and not owner_approved:
            return ControlDecision.APPROVAL_REQUIRED
        return ControlDecision.ALLOW

    def consume(self, command: ControlCommand, *, owner_approved: bool = False) -> ControlDecision:
        decision = self.decide(command, owner_approved=owner_approved)
        if decision is ControlDecision.ALLOW:
            self._pending.pop(command.command_id, None)
        return decision
