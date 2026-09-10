"""Core autonomous execution loop with explicit safety boundaries."""

from __future__ import annotations

from uuid import uuid4

from .contracts import ActionRequest, ActionResult, ActionRisk, Event
from .decision import DecisionEngine
from .events import RuntimeEvent
from .permissions import PermissionDenied, PermissionPolicy
from .planner.engine import Plan, PlanStep, Planner
from .runtime import RuntimeContext


class Orchestrator:
    """Coordinates PLAN -> PERMISSION -> ACT -> VERIFY -> RECORD."""

    def __init__(self, permission_policy: PermissionPolicy | None = None, runtime: RuntimeContext | None = None) -> None:
        self.runtime = runtime or RuntimeContext()
        if permission_policy is not None:
            self.runtime.permissions = permission_policy
        self.permissions = self.runtime.permissions
        self.planner = Planner()
        self.decisions = DecisionEngine()

    def authorize(self, request: ActionRequest, *, owner_approved: bool = False) -> bool:
        return self.permissions.check(request, owner_approved=owner_approved)

    def register(self, action: str, handler) -> None:
        self.runtime.register(action, handler)

    def record_event(self, event: Event) -> Event:
        self.runtime.events.publish(RuntimeEvent(name=event.name, payload=dict(event.payload), created_at=event.created_at))
        return event

    def result(self, request: ActionRequest, *, success: bool, message: str = "", data=None) -> ActionResult:
        return ActionResult(success=success, action=request.action, message=message, data={} if data is None else data)

    def execute(self, request: ActionRequest, *, owner_approved: bool = False, value: float = 0.0) -> ActionResult:
        """Execute one registered action through the core safety path."""
        self.runtime.increment("requests.total")
        self.record_event(Event("action.requested", {"action": request.action}))
        try:
            decision = self.decisions.decide(request, value=value)
            if not decision.allowed:
                self.runtime.increment("requests.rejected")
                return self.result(request, success=False, message=decision.reason)
            self.authorize(request, owner_approved=owner_approved)
            handler = self.runtime.handler(request.action)
            if handler is None:
                self.runtime.increment("requests.unknown_action")
                return self.result(request, success=False, message="No registered handler for action")
            self.record_event(Event("action.authorized", {"action": request.action}))
            output = handler(dict(request.payload))
            if output is None:
                self.runtime.increment("requests.verification_failed")
                self.record_event(Event("action.verification_failed", {"action": request.action}))
                return self.result(request, success=False, message="Action produced no verifiable result")
            self.runtime.increment("requests.succeeded")
            self.record_event(Event("action.completed", {"action": request.action}))
            return self.result(request, success=True, message="Action completed", data={"output": output})
        except PermissionDenied as exc:
            self.runtime.increment("requests.denied")
            self.record_event(Event("action.denied", {"action": request.action, "reason": str(exc)}))
            return self.result(request, success=False, message=str(exc))
        except Exception as exc:
            self.runtime.increment("requests.failed")
            self.record_event(Event("action.failed", {"action": request.action, "error": type(exc).__name__}))
            return self.result(request, success=False, message=f"Action failed safely: {exc}")

    def run_plan(self, plan: Plan, *, owner_approved: bool = False) -> tuple[ActionResult, ...]:
        results: list[ActionResult] = []
        for step in plan.steps:
            payload = dict(step.payload)
            risk = payload.pop("_risk", ActionRisk.LOW)
            if not isinstance(risk, ActionRisk):
                risk = ActionRisk.LOW
            request = ActionRequest(action=step.action, risk=risk, reason=step.reason, payload=payload)
            result = self.execute(request, owner_approved=owner_approved)
            results.append(result)
            if not result.success:
                break
        return tuple(results)

    def plan_and_run(self, goal: str, steps: list[PlanStep], *, owner_approved: bool = False) -> tuple[ActionResult, ...]:
        plan = self.planner.plan(str(uuid4()), goal, steps)
        self.record_event(Event("plan.created", {"task_id": plan.task_id, "goal": plan.goal, "steps": len(plan.steps)}))
        return self.run_plan(plan, owner_approved=owner_approved)
