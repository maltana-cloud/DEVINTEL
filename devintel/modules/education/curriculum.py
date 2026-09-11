"""Deterministic curriculum planning primitives."""
from __future__ import annotations

from collections import defaultdict, deque
from dataclasses import dataclass
from typing import Iterable

from .contracts import Lesson, Skill


@dataclass(frozen=True)
class CurriculumVersion:
    version: str
    domain: str
    lesson_ids: tuple[str, ...]
    description: str = ""

    def __post_init__(self) -> None:
        if not self.version.strip() or not self.domain.strip():
            raise ValueError("version and domain are required")
        if not self.lesson_ids:
            raise ValueError("curriculum version requires lessons")


def prerequisite_skill_order(skills: Iterable[Skill]) -> tuple[str, ...]:
    """Return a stable topological order; reject cycles and missing prerequisites."""
    items = tuple(skills)
    known = {skill.skill_id for skill in items}
    indegree = {skill.skill_id: 0 for skill in items}
    edges: dict[str, list[str]] = defaultdict(list)
    for skill in items:
        for prerequisite in skill.prerequisites:
            if prerequisite not in known:
                raise ValueError(f"unknown prerequisite: {prerequisite}")
            edges[prerequisite].append(skill.skill_id)
            indegree[skill.skill_id] += 1
    queue = deque(sorted((sid for sid, degree in indegree.items() if degree == 0)))
    ordered: list[str] = []
    while queue:
        current = queue.popleft()
        ordered.append(current)
        for child in sorted(edges[current]):
            indegree[child] -= 1
            if indegree[child] == 0:
                queue.append(child)
    if len(ordered) != len(items):
        raise ValueError("skill prerequisite cycle detected")
    return tuple(ordered)


def lesson_goal_score(lesson: Lesson, goals: Iterable[str]) -> float:
    """Score explicit goal tags first, then use conservative text matching."""
    normalized = tuple(g.strip().lower() for g in goals if isinstance(g, str) and g.strip())
    if not normalized:
        return 0.0
    tags = {str(tag).strip().lower() for tag in lesson.metadata.get("goal_tags", ()) if str(tag).strip()}
    if tags:
        return sum(goal in tags for goal in normalized) / len(normalized)
    text = f"{lesson.title} {lesson.content}".lower()
    return sum(goal in text for goal in normalized) / len(normalized)
