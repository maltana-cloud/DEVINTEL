"""Education quality, safety, and monetization boundaries."""
from __future__ import annotations

from dataclasses import dataclass

from .contracts import Course, Lesson, SkillLevel


@dataclass(frozen=True)
class EducationPolicy:
    min_lesson_confidence: float = 0.60
    allow_premium_offers: bool = True

    def __post_init__(self) -> None:
        if not 0.0 <= self.min_lesson_confidence <= 1.0:
            raise ValueError("min_lesson_confidence must be between 0 and 1")

    def lesson_allowed(self, lesson: Lesson) -> bool:
        confidence = lesson.metadata.get("confidence", 0.0)
        try:
            value = float(confidence)
        except (TypeError, ValueError):
            return False
        if not 0.0 <= value <= 1.0:
            return False
        # Educational claims must retain provenance. High confidence never
        # substitutes for evidence, because education is a downstream use of
        # the truth/verification boundary.
        if not lesson.evidence_urls or not all(u.strip() for u in lesson.evidence_urls):
            return False
        return value >= self.min_lesson_confidence

    def course_allowed(self, course: Course) -> bool:
        return (
            (not course.premium or self.allow_premium_offers)
            and course.price_minor >= 0
            and len(course.currency) == 3
        )

    @staticmethod
    def next_level(level: SkillLevel) -> SkillLevel:
        order = (
            SkillLevel.BEGINNER,
            SkillLevel.INTERMEDIATE,
            SkillLevel.ADVANCED,
            SkillLevel.EXPERT,
        )
        index = order.index(level)
        return order[min(index + 1, len(order) - 1)]
