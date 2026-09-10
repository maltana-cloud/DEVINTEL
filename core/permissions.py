"""Fail-closed permission policy for core actions."""

from __future__ import annotations

from dataclasses import dataclass

from .contracts import ActionRisk, SecurityState


@dataclass(frozen=True)
class PermissionDecision:
    allowed: bool
    reason: str


class PermissionPolicy:
    """Central authority for deciding whether an action may execute."""

    def check(
        self,
        risk: ActionRisk,
        *,
        owner_approved: bool = False,
        security_state: SecurityState = SecurityState.NORMAL,
    ) -> PermissionDecision:
        if security_state in {
            SecurityState.CONTAINMENT,
            SecurityState.RECOVERY,
        }:
            return PermissionDecision(False, "security state blocks autonomous action")

        if risk is ActionRisk.EMERGENCY_STOP:
            return PermissionDecision(True, "emergency control is always executable")

        if risk is ActionRisk.OWNER_APPROVAL and not owner_approved:
            return PermissionDecision(False, "owner approval required")

        if security_state is SecurityState.SAFE_DEGRADED and risk is not ActionRisk.AUTOMATIC:
            return PermissionDecision(False, "safe-degraded mode permits automatic actions only")

        return PermissionDecision(True, "action permitted by policy")
