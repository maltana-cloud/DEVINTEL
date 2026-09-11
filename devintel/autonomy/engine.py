"""Bounded OBSERVE→UNDERSTAND→PLAN→PERMISSION→ACT→VERIFY→RECORD loop."""
from __future__ import annotations
from collections.abc import Callable, Sequence
from uuid import uuid4
from ..core.orchestrator import Orchestrator
from ..core.contracts import ActionRequest, ActionResult
from .contracts import AutonomousCycle, AutonomyPhase, Observation

Observer = Callable[[str], Sequence[Observation]]
Planner = Callable[[str, Sequence[Observation]], Sequence[ActionRequest]]
Verifier = Callable[[str, Sequence[ActionResult]], bool]
Recorder = Callable[[AutonomousCycle], None]

class AutonomousEngine:
    """Runs finite cycles only; it never creates authority outside Core's policy."""
    def __init__(self, orchestrator: Orchestrator, observer: Observer, planner: Planner, verifier: Verifier, recorder: Recorder | None = None) -> None:
        self.orchestrator = orchestrator; self.observer = observer; self.planner = planner; self.verifier = verifier; self.recorder = recorder
    def run_once(self, scope_id: str) -> AutonomousCycle:
        scope = scope_id.strip() if isinstance(scope_id, str) else ""
        if not scope: raise ValueError("scope_id is required")
        phases = [AutonomyPhase.OBSERVE]
        observations = tuple(self.observer(scope))
        if not all(isinstance(item, Observation) and item.scope_id == scope for item in observations):
            cycle = AutonomousCycle(uuid4().hex, scope, tuple(phases), 0, 0, 0, False, True, "invalid or cross-scope observation")
            if self.recorder: self.recorder(cycle)
            return cycle
        phases.extend((AutonomyPhase.UNDERSTAND, AutonomyPhase.PLAN))
        actions = tuple(self.planner(scope, observations))
        if not all(isinstance(item, ActionRequest) and item.payload.get("_scope_id") == scope for item in actions):
            cycle = AutonomousCycle(uuid4().hex, scope, tuple(phases), len(actions), 0, 0, False, True, "invalid or cross-scope plan")
            if self.recorder: self.recorder(cycle)
            return cycle
        phases.extend((AutonomyPhase.PERMISSION, AutonomyPhase.ACT))
        results: list[ActionResult] = []
        for action in actions:
            payload = dict(action.payload); payload.pop("_scope_id", None)
            scoped_action = ActionRequest(action.action, action.risk, action.reason, payload)
            results.append(self.orchestrator.execute(scoped_action))
        succeeded = sum(1 for result in results if result.success); failed = len(results) - succeeded
        phases.append(AutonomyPhase.VERIFY); verified = bool(self.verifier(scope, tuple(results)))
        phases.append(AutonomyPhase.RECORD)
        cycle = AutonomousCycle(uuid4().hex, scope, tuple(phases), len(actions), succeeded, failed, verified)
        if self.recorder: self.recorder(cycle)
        return cycle
