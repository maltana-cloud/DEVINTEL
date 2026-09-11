from devintel.autonomy import AutonomousEngine, AutonomyPhase, Observation
from devintel.core.contracts import ActionRequest
from devintel.core.orchestrator import Orchestrator

def test_autonomous_loop_completes_bounded_cycle():
    runtime = Orchestrator()
    runtime.register("ping", lambda payload: {"ok": True})
    engine = AutonomousEngine(
        runtime,
        observer=lambda scope: [Observation(scope, "signal", {"value": 1})],
        planner=lambda scope, observations: [ActionRequest("ping", reason="safe test", payload={"_scope_id": scope})],
        verifier=lambda scope, results: len(results) == 1 and results[0].success,
    )
    cycle = engine.run_once("scope")
    assert cycle.verified is True
    assert cycle.actions_succeeded == 1
    assert cycle.completed_phases == tuple(AutonomyPhase)

def test_autonomous_loop_rejects_cross_scope_plan_before_acting():
    called = []
    runtime = Orchestrator()
    runtime.register("ping", lambda payload: called.append(payload))
    engine = AutonomousEngine(
        runtime,
        observer=lambda scope: [Observation(scope, "signal")],
        planner=lambda scope, observations: [ActionRequest("ping", payload={"_scope_id": "other"})],
        verifier=lambda scope, results: False,
    )
    cycle = engine.run_once("scope")
    assert cycle.stopped is True
    assert cycle.actions_succeeded == 0
    assert called == []
