"""Deterministic task planning primitives."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class PlanStep:
    id: str
    action: str
    reason: str = ""
    payload: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class Plan:
    task_id: str
    goal: str
    steps: tuple[PlanStep, ...]


class Planner:
    """Creates explicit plans without executing them."""

    def plan(self, task_id: str, goal: str, steps: list[PlanStep] | tuple[PlanStep, ...]) -> Plan:
        if not task_id.strip() or not goal.strip():
            raise ValueError("task_id and goal are required")
        if not steps:
            raise ValueError("a plan must contain at least one step")
        seen: set[str] = set()
        normalized: list[PlanStep] = []
        for step in steps:
            if not step.id or not step.action:
                raise ValueError("every plan step requires an id and action")
            if step.id in seen:
                raise ValueError(f"duplicate plan step: {step.id}")
            seen.add(step.id)
            normalized.append(step)
        return Plan(task_id=task_id, goal=goal, steps=tuple(normalized))
