"""Centralized permission policy for autonomous actions."""

from .contracts import ActionRequest, ActionRisk


class PermissionDenied(Exception):
    """Raised when an action is outside the configured autonomy boundary."""


class PermissionPolicy:
    """Deterministic first-pass policy; configuration can replace this later."""

    def __init__(self, *, emergency_stop: bool = False) -> None:
        self.emergency_stop = emergency_stop

    def check(self, request: ActionRequest) -> bool:
        if self.emergency_stop:
            raise PermissionDenied("Emergency stop is active")
        if request.risk in {ActionRisk.HIGH, ActionRisk.CRITICAL}:
            raise PermissionDenied("Owner approval required for high-risk actions")
        return True
