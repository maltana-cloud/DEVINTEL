"""Core autonomous execution engine for DEVINTEL.

The engine coordinates the locked loop without embedding any domain or provider
logic. External modules plug into observe/understand/plan/act/verify hooks.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from .contracts import ActionRisk, SecurityState
from .events import Event, EventBus
from .permissions import PermissionPolicy
from .state import StateStore


@dataclass(frozen=True)
class CycleResult:
    cycle: int
    action: str | None
    acted: bool
    reason: str
    verified: bool


class CoreEngine:
    """Runs one bounded autonomous cycle at a time."""

    def __init__(
        self,
        *,
        events: EventBus | None = None,
        state: StateStore | None = None,
        permissions: PermissionPolicy | None = None,
    ) -> None:
        self.events = events or EventBus()
        self.state = state or StateStore()
        self.permissions = permissions or PermissionPolicy()

    def cycle(
        self,
        *,
        observe: Callable[[], Any],
        understand: Callable[[Any], Any],
        plan: Callable[[Any], Any],
        act: Callable[[Any], Any],
        verify: Callable[[Any, Any], bool],
        risk: ActionRisk = ActionRisk.AUTOMATIC,
        owner_approved: bool = False,
    ) -> CycleResult:
        number = self.state.begin_cycle()
        self.events.publish(Event("cycle.started", {"cycle": number}))
        action_name: str | None = None
        try:
            observation = observe()
            self.events.publish(Event("cycle.observed", observation))
            understanding = understand(observation)
            self.events.publish(Event("cycle.understood", understanding))
            decision = plan(understanding)
            self.events.publish(Event("cycle.planned", decision))

            permission = self.permissions.check(
                risk,
                owner_approved=owner_approved,
                security_state=self.state.snapshot().security,
            )
            if not permission.allowed:
                self.events.publish(Event("cycle.blocked", permission.reason))
                return CycleResult(number, None, False, permission.reason, False)

            action_name = getattr(decision, "name", None) or str(decision)
            result = act(decision)
            verified = bool(verify(decision, result))
            if not verified:
                self.state.set_security(SecurityState.WATCH)
                self.events.publish(Event("cycle.verification_failed", {"cycle": number}))
                return CycleResult(number, action_name, True, "action verification failed", False)

            self.events.publish(Event("cycle.completed", {"cycle": number}))
            return CycleResult(number, action_name, True, "action completed and verified", True)
        finally:
            self.state.end_cycle(action_name)
