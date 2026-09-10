"""Provider-neutral planning primitives for DEVINTEL."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Iterable


@dataclass(frozen=True)
class PlanStep:
    name: str
    action: str
    risk: str = "automatic"


@dataclass(frozen=True)
class Plan:
    goal: str
    steps: tuple[PlanStep, ...]


class Planner:
    """Turns explicit step definitions into an immutable execution plan."""

    def build(self, goal: str, steps: Iterable[PlanStep]) -> Plan:
        goal = goal.strip()
        normalized = tuple(steps)
        if not goal:
            raise ValueError("goal is required")
        if not normalized:
            raise ValueError("a plan must contain at least one step")
        if any(not step.name.strip() or not step.action.strip() for step in normalized):
            raise ValueError("every plan step needs a name and action")
        return Plan(goal=goal, steps=normalized)
