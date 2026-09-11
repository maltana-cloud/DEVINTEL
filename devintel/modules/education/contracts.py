"""Contracts for domain-scoped education, courses, practice, and mentorship."""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import StrEnum
from typing import Any

class EducationMode(StrEnum):
    COURSE = "course"
    MENTORSHIP = "mentorship"
    PRACTICE = "practice"
    APPRENTICESHIP = "apprenticeship"

class SkillLevel(StrEnum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"

class AssessmentResult(StrEnum):
    PASS = "pass"
    NEEDS_PRACTICE = "needs_practice"
    FAIL = "fail"

@dataclass(frozen=True)
class Skill:
    skill_id: str
    name: str
    domain: str
    prerequisites: tuple[str, ...] = ()
    metadata: dict[str, Any] = field(default_factory=dict)
    def __post_init__(self) -> None:
        if not self.skill_id.strip() or not self.name.strip() or not self.domain.strip():
            raise ValueError("skill_id, name, and domain are required")

@dataclass(frozen=True)
class Lesson:
    lesson_id: str
    title: str
    domain: str
    skill_ids: tuple[str, ...]
    content: str
    evidence_urls: tuple[str, ...] = ()
    level: SkillLevel = SkillLevel.BEGINNER
    metadata: dict[str, Any] = field(default_factory=dict)
    curriculum_version: str = "1"
    def __post_init__(self) -> None:
        if not self.lesson_id.strip() or not self.title.strip() or not self.domain.strip() or not self.content.strip():
            raise ValueError("lesson_id, title, domain, and content are required")
        if not self.skill_ids: raise ValueError("at least one skill is required")
        if any(not u.strip() for u in self.evidence_urls): raise ValueError("evidence URLs must be non-empty")
        if not self.curriculum_version.strip(): raise ValueError("curriculum_version is required")

@dataclass(frozen=True)
class Course:
    course_id: str
    title: str
    domain: str
    lessons: tuple[str, ...]
    description: str
    level: SkillLevel = SkillLevel.BEGINNER
    premium: bool = False
    price_minor: int = 0
    currency: str = "NGN"
    metadata: dict[str, Any] = field(default_factory=dict)
    def __post_init__(self) -> None:
        if not self.course_id.strip() or not self.title.strip() or not self.domain.strip() or not self.description.strip():
            raise ValueError("course_id, title, domain, and description are required")
        if not self.lessons: raise ValueError("course must contain lessons")
        if self.price_minor < 0 or len(self.currency) != 3: raise ValueError("invalid course price")

@dataclass(frozen=True)
class LearnerProgress:
    scope_id: str
    learner_id: str
    domain: str
    completed_lessons: tuple[str, ...] = ()
    mastered_skills: tuple[str, ...] = ()
    current_level: SkillLevel = SkillLevel.BEGINNER
    goals: tuple[str, ...] = ()
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    def __post_init__(self) -> None:
        if not self.scope_id.strip() or not self.learner_id.strip() or not self.domain.strip():
            raise ValueError("scope_id, learner_id, and domain are required")
        if self.updated_at.tzinfo is None: raise ValueError("updated_at must be timezone-aware")

@dataclass(frozen=True)
class PracticeTask:
    task_id: str
    domain: str
    skill_id: str
    prompt: str
    expected_outcome: str
    level: SkillLevel = SkillLevel.BEGINNER
    metadata: dict[str, Any] = field(default_factory=dict)
    def __post_init__(self) -> None:
        if not all(isinstance(v, str) and v.strip() for v in (self.task_id, self.domain, self.skill_id, self.prompt, self.expected_outcome)):
            raise ValueError("practice task fields are required")

@dataclass(frozen=True)
class Assessment:
    assessment_id: str
    scope_id: str
    learner_id: str
    task_id: str
    result: AssessmentResult
    score: float
    feedback: str
    assessed_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    domain: str = ""
    skill_id: str = ""
    def __post_init__(self) -> None:
        if not self.assessment_id.strip() or not self.scope_id.strip() or not self.learner_id.strip() or not self.task_id.strip() or not self.feedback.strip():
            raise ValueError("assessment identifiers and feedback are required")
        if not 0.0 <= self.score <= 1.0: raise ValueError("score must be between 0 and 1")
        if self.assessed_at.tzinfo is None: raise ValueError("assessed_at must be timezone-aware")
        if self.domain and not self.domain.strip(): raise ValueError("domain must be non-empty when supplied")
        if self.skill_id and not self.skill_id.strip(): raise ValueError("skill_id must be non-empty when supplied")

@dataclass(frozen=True)
class MentorshipSession:
    session_id: str
    scope_id: str
    learner_id: str
    domain: str
    goal: str
    mode: EducationMode = EducationMode.MENTORSHIP
    level: SkillLevel = SkillLevel.BEGINNER
    metadata: dict[str, Any] = field(default_factory=dict)
    def __post_init__(self) -> None:
        if not all(isinstance(v, str) and v.strip() for v in (self.session_id, self.scope_id, self.learner_id, self.domain, self.goal)):
            raise ValueError("mentorship session fields are required")
        if self.mode is not EducationMode.MENTORSHIP: raise ValueError("mentorship session must use mentorship mode")

@dataclass(frozen=True)
class LearningPath:
    path_id: str
    scope_id: str
    learner_id: str
    domain: str
    skill_ids: tuple[str, ...]
    lesson_ids: tuple[str, ...]
    rationale: str
    curriculum_version: str = "1"
    def __post_init__(self) -> None:
        if not all(isinstance(v, str) and v.strip() for v in (self.path_id, self.scope_id, self.learner_id, self.domain, self.rationale)):
            raise ValueError("learning path fields are required")
        if not self.skill_ids or not self.lesson_ids: raise ValueError("learning path cannot be empty")
        if not self.curriculum_version.strip(): raise ValueError("curriculum_version is required")
