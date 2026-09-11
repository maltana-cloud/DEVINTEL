"""Provider-independent education and mentorship orchestration."""
from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Sequence
from .contracts import Assessment, AssessmentResult, Course, EducationMode, LearnerProgress, Lesson, LearningPath, SkillLevel
from .curriculum import CurriculumVersion, lesson_goal_score, prerequisite_skill_order
from .policy import EducationPolicy
from .providers import EducationProvider
from .store import EducationStore

@dataclass(frozen=True)
class EducationPlan:
    scope_id: str
    learner_id: str
    domain: str
    mode: EducationMode
    level: SkillLevel
    path: LearningPath

class EducationEngine:
    """Builds adaptive learning paths; content authority stays with verified inputs/providers."""
    def __init__(self, store: EducationStore | None = None, policy: EducationPolicy | None = None) -> None:
        self.store = store or EducationStore()
        self.policy = policy or EducationPolicy()

    def register_lesson(self, lesson: Lesson) -> Lesson:
        if not self.policy.lesson_allowed(lesson): raise ValueError("lesson does not satisfy education quality policy")
        return self.store.add_lesson(lesson)

    def register_course(self, course: Course) -> Course:
        if not self.policy.course_allowed(course): raise ValueError("course does not satisfy education policy")
        return self.store.add_course(course)

    def register_curriculum(self, curriculum: CurriculumVersion) -> CurriculumVersion:
        if curriculum.domain != curriculum.domain.strip(): raise ValueError("invalid curriculum domain")
        for lesson_id in curriculum.lesson_ids:
            lesson = next((x for x in self.store.lessons(curriculum.domain) if x.lesson_id == lesson_id), None)
            if lesson is None: raise ValueError(f"unknown curriculum lesson: {lesson_id}")
            if lesson.curriculum_version != curriculum.version: raise ValueError("lesson curriculum version mismatch")
        return self.store.save_curriculum(curriculum)

    def build_path(self, scope_id: str, learner_id: str, domain: str, *, goals: Sequence[str] = (), level: SkillLevel = SkillLevel.BEGINNER, mode: EducationMode = EducationMode.COURSE) -> EducationPlan:
        scope = scope_id.strip() if isinstance(scope_id, str) else ""
        learner = learner_id.strip() if isinstance(learner_id, str) else ""
        subject = domain.strip() if isinstance(domain, str) else ""
        if not scope or not learner or not subject: raise ValueError("scope_id, learner_id, and domain are required")
        progress = self.store.progress(scope, learner, subject)
        completed = set(progress.completed_lessons) if progress else set()
        mastered = set(progress.mastered_skills) if progress else set()
        skills = self.store.skills(subject)
        ordered_skills = prerequisite_skill_order(skills)
        available_skills = {sid for sid in ordered_skills if sid not in mastered}
        lessons = [x for x in self.store.lessons(subject) if x.level == level and x.lesson_id not in completed]
        lessons.sort(key=lambda x: (-lesson_goal_score(x, goals), ordered_skills.index(x.skill_ids[0]) if x.skill_ids[0] in ordered_skills else len(ordered_skills), x.lesson_id))
        selected: list[Lesson] = []
        unlocked = set(mastered)
        for item in lessons:
            if all(prereq in unlocked or prereq not in {s.skill_id for s in skills} for skill_id in item.skill_ids for prereq in next((s.prerequisites for s in skills if s.skill_id == skill_id), ())):
                selected.append(item)
                unlocked.update(item.skill_ids)
        if not selected: raise ValueError("no suitable lessons available")
        lesson_ids = tuple(x.lesson_id for x in selected)
        skill_ids = tuple(sid for sid in ordered_skills if sid in available_skills and any(sid in x.skill_ids for x in selected))
        rationale = "Prioritized goal relevance, excluded completed/mastered work, and respected skill prerequisites."
        version = selected[0].curriculum_version
        path = LearningPath(f"{scope}:{learner}:{subject}:{level.value}", scope, learner, subject, skill_ids, lesson_ids, rationale, version)
        self.store.save_path(path)
        return EducationPlan(scope, learner, subject, mode, level, path)

    def record_assessment(self, assessment: Assessment) -> LearnerProgress:
        if not assessment.domain or not assessment.skill_id: raise ValueError("assessment domain and skill_id are required")
        self.store.add_assessment(assessment)
        current = self.store.progress(assessment.scope_id, assessment.learner_id, assessment.domain)
        completed = list(current.completed_lessons) if current else []
        mastered = set(current.mastered_skills) if current else set()
        if assessment.result is AssessmentResult.PASS and assessment.skill_id not in mastered:
            mastered.add(assessment.skill_id)
        if assessment.result is AssessmentResult.PASS and assessment.task_id not in completed:
            completed.append(assessment.task_id)
        goals = current.goals if current else ()
        level = current.current_level if current else SkillLevel.BEGINNER
        updated = LearnerProgress(assessment.scope_id, assessment.learner_id, assessment.domain, tuple(completed), tuple(sorted(mastered)), level, goals, datetime.now(timezone.utc))
        return self.store.save_progress(updated)

    def progress(self, scope_id: str, learner_id: str, domain: str) -> LearnerProgress | None:
        return self.store.progress(scope_id, learner_id, domain)
