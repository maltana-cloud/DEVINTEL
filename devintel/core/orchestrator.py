"""Minimal orchestration boundary for the DEVINTEL action loop."""

from .contracts import ActionRequest, ActionResult, Event
from .permissions import PermissionPolicy


class Orchestrator:
    """Coordinates planning/execution without coupling modules together."""

    def __init__(self, permission_policy: PermissionPolicy | None = None) -> None:
        self.permissions = permission_policy or PermissionPolicy()

    def authorize(self, request: ActionRequest) -> bool:
        return self.permissions.check(request)

    def record_event(self, event: Event) -> Event:
        # Persistence/event bus will be injected in a later module milestone.
        return event

    def result(self, request: ActionRequest, *, success: bool, message: str = "", data=None) -> ActionResult:
        return ActionResult(
            success=success,
            action=request.action,
            message=message,
            data={} if data is None else data,
        )
