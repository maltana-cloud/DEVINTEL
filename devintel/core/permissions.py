"""Centralized, fail-closed permission policy for autonomous actions."""

from .contracts import ActionRequest, ActionRisk


class PermissionDenied(Exception):
    """Raised when an action is outside the configured autonomy boundary."""


class PermissionPolicy:
    """Enforces authority boundaries independently of intelligence decisions."""

    def __init__(self, *, emergency_stop: bool = False) -> None:
        self.emergency_stop = emergency_stop

    def check(self, request: ActionRequest, *, owner_approved: bool = False) -> bool:
        if not isinstance(request.risk, ActionRisk):
            raise PermissionDenied("Unknown action risk")
        if self.emergency_stop:
            raise PermissionDenied("Emergency stop is active")
        if request.risk in {ActionRisk.HIGH, ActionRisk.CRITICAL} and not owner_approved:
            raise PermissionDenied("Owner approval required for high-risk actions")
        return True
