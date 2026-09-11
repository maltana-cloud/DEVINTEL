"""Provider boundary for channel-specific education content."""
from __future__ import annotations

from typing import Protocol, Sequence

from .contracts import Lesson, Skill, SkillLevel


class EducationProvider(Protocol):
    """Host-controlled source for evidence-backed education material."""

    def skills(self, domain: str) -> Sequence[Skill]: ...

    def lessons(self, domain: str, level: SkillLevel, goals: Sequence[str]) -> Sequence[Lesson]: ...
