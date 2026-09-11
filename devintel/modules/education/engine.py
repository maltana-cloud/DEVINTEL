"""Provider-independent education and mentorship orchestration."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Protocol, Sequence
from .contracts import Course, EducationMode, LearnerProgress, Lesson, LearningPath, SkillLevel
from .policy import EducationPolicy
from .store import EducationStore

class EducationSource(Protocol):
    def discover_skills(self, domain: str) -> Sequence[object]: ...
    def create_lessons(self, domain: str, level: SkillLevel, goals: Sequence[str]) -> Sequence[object]: ...

@dataclass(frozen=True)
class EducationPlan:
    scope_id: str
    learner_id: str
    domain: str
    mode: EducationMode
    level: SkillLevel
    path: LearningPath

class EducationEngine:
    """Builds bounded learning paths; content authority stays with verified inputs/providers."""
    def __init__(self, store: EducationStore | None = None, policy: EducationPolicy | None = None) -> None:
        self.store = store or EducationStore()
        self.policy = policy or EducationPolicy()

    def register_lesson(self, lesson: Lesson) -> Lesson:
        if not self.policy.lesson_allowed(lesson):
            raise ValueError("lesson does not satisfy education quality policy")
        return self.store.add_lesson(lesson)

    def register_course(self, course: Course) -> Course:
        if not self.policy.course_allowed(course):
            raise ValueError("course does not satisfy education policy")
        return self.store.add_course(course)

    def build_path(self, scope_id: str, learner_id: str, domain: str, *, goals: Sequence[str] = (), level: SkillLevel = SkillLevel.BEGINNER, mode: EducationMode = EducationMode.COURSE) -> EducationPlan:
        scope = scope_id.strip() if isinstance(scope_id, str) else ""
        learner = learner_id.strip() if isinstance(learner_id, str) else ""
        subject = domain.strip() if isinstance(domain, str) else ""
        if not scope or not learner or not subject: raise ValueError("scope_id, learner_id, and domain are required")
        progress = self.store.progress(scope, learner, subject)
        completed = set(progress.completed_lessons) if progress else set()
        lessons = tuple(x for x in self.store.lessons(subject) if x.level == level and x.lesson_id not in completed)
        skills = self.store.skills(subject)
        skill_ids = tuple(x.skill_id for x in skills if not progress or x.skill_id not in progress.mastered_skills)
        lesson_ids = tuple(x.lesson_id for x in lessons)
        if not lesson_ids: raise ValueError("no suitable lessons available")
        path = LearningPath(f"{scope}:{learner}:{subject}:{level.value}", scope, learner, subject, skill_ids, lesson_ids, "Selected uncompleted lessons and unmastered skills for the learner's current scope and level.")
        self.store.save_path(path)
        return EducationPlan(scope, learner, subject, mode, level, path)

    def progress(self, scope_id: str, learner_id: str, domain: str) -> LearnerProgress | None:
        return self.store.progress(scope_id, learner_id, domain)
