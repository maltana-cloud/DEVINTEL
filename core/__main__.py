"""Smoke-test entry point: python -m core."""

from .contracts import ActionRisk
from .engine import CoreEngine
from .planner import PlanStep, Planner


def main() -> None:
    planner = Planner()
    engine = CoreEngine()

    def observe():
        return {"signal": "core-smoke-test"}

    def understand(data):
        return data

    def plan(data):
        return planner.build(
            "complete core smoke test",
            [PlanStep("smoke", "run_core_smoke_test")],
        ).steps[0]

    def act(step):
        return {"executed": step.action}

    def verify(step, result):
        return result.get("executed") == step.action

    result = engine.cycle(
        observe=observe,
        understand=understand,
        plan=plan,
        act=act,
        verify=verify,
        risk=ActionRisk.AUTOMATIC,
    )
    print(result)


if __name__ == "__main__":
    main()
