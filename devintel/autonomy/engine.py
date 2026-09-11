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
    """Runs finite cycles only; failures stop one cycle without escaping its boundary."""
    def __init__(self, orchestrator: Orchestrator, observer: Observer, planner: Planner, verifier: Verifier, recorder: Recorder | None = None) -> None:
        self.orchestrator = orchestrator; self.observer = observer; self.planner = planner; self.verifier = verifier; self.recorder = recorder
    def _finish(self, scope: str, phases: list[AutonomyPhase], planned: int, succeeded: int, failed: int, verified: bool, reason: str = "") -> AutonomousCycle:
        cycle = AutonomousCycle(uuid4().hex, scope, tuple(phases), planned, succeeded, failed, verified, bool(reason), reason)
        if self.recorder:
            try: self.recorder(cycle)
            except Exception: pass
        return cycle
    def run_once(self, scope_id: str) -> AutonomousCycle:
        scope = scope_id.strip() if isinstance(scope_id, str) else ""
        if not scope: raise ValueError("scope_id is required")
        phases = [AutonomyPhase.OBSERVE]
        try:
            observations = tuple(self.observer(scope))
        except Exception as exc:
            return self._finish(scope, phases, 0, 0, 0, False, f"observation failed: {type(exc).__name__}")
        if not all(isinstance(item, Observation) and item.scope_id == scope for item in observations):
            return self._finish(scope, phases, 0, 0, 0, False, "invalid or cross-scope observation")
        phases.extend((AutonomyPhase.UNDERSTAND, AutonomyPhase.PLAN))
        try:
            actions = tuple(self.planner(scope, observations))
        except Exception as exc:
            return self._finish(scope, phases, 0, 0, 0, False, f"planning failed: {type(exc).__name__}")
        if not all(isinstance(item, ActionRequest) and item.payload.get("_scope_id") == scope for item in actions):
            return self._finish(scope, phases, len(actions), 0, 0, False, "invalid or cross-scope plan")
        phases.extend((AutonomyPhase.PERMISSION, AutonomyPhase.ACT))
        results: list[ActionResult] = []
        for action in actions:
            payload = dict(action.payload); payload.pop("_scope_id", None)
            scoped_action = ActionRequest(action.action, action.risk, action.reason, payload)
            results.append(self.orchestrator.execute(scoped_action))
        succeeded = sum(1 for result in results if result.success); failed = len(results) - succeeded
        phases.append(AutonomyPhase.VERIFY)
        try:
            verified = bool(self.verifier(scope, tuple(results)))
        except Exception as exc:
            return self._finish(scope, phases, len(actions), succeeded, failed, False, f"verification failed: {type(exc).__name__}")
        phases.append(AutonomyPhase.RECORD)
        return self._finish(scope, phases, len(actions), succeeded, failed, verified)
