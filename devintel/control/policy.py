"""Fail-closed policy for owner control commands."""
from __future__ import annotations

from .contracts import ControlCommand, ControlDecision


class OwnerControlPolicy:
    """Classify control requests without executing them or granting authority."""

    def decide(self, command: ControlCommand, *, owner_approved: bool = False) -> ControlDecision:
        if command.requires_owner_approval and not owner_approved:
            return ControlDecision.APPROVAL_REQUIRED
        return ControlDecision.ALLOW
