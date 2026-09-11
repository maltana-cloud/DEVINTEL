"""Bounded, thread-safe education state with strict learner scope isolation."""
from __future__ import annotations
from collections import OrderedDict
from threading import RLock
from .contracts import Assessment, Course, LearnerProgress, Lesson, LearningPath, Skill
from .curriculum import CurriculumVersion

class EducationStore:
    def __init__(self, max_items: int = 10000) -> None:
        if max_items < 1: raise ValueError("max_items must be positive")
        self.max_items = max_items
        self._lock = RLock()
        self._skills: OrderedDict[str, Skill] = OrderedDict()
        self._lessons: OrderedDict[str, Lesson] = OrderedDict()
        self._courses: OrderedDict[str, Course] = OrderedDict()
        self._progress: OrderedDict[tuple[str, str, str], LearnerProgress] = OrderedDict()
        self._paths: OrderedDict[tuple[str, str, str], LearningPath] = OrderedDict()
        self._curricula: OrderedDict[tuple[str, str], CurriculumVersion] = OrderedDict()
        self._assessments: list[Assessment] = []

    @staticmethod
    def _put(store: OrderedDict, key, item, limit: int) -> None:
        store[key] = item
        store.move_to_end(key)
        while len(store) > limit:
            store.popitem(last=False)

    def add_skill(self, item: Skill) -> Skill:
        with self._lock: self._put(self._skills, item.skill_id, item, self.max_items)
        return item

    def add_lesson(self, item: Lesson) -> Lesson:
        with self._lock: self._put(self._lessons, item.lesson_id, item, self.max_items)
        return item

    def add_course(self, item: Course) -> Course:
        with self._lock: self._put(self._courses, item.course_id, item, self.max_items)
        return item

    def save_progress(self, item: LearnerProgress) -> LearnerProgress:
        key = (item.scope_id, item.learner_id, item.domain)
        with self._lock: self._put(self._progress, key, item, self.max_items)
        return item

    def save_path(self, item: LearningPath) -> LearningPath:
        key = (item.scope_id, item.learner_id, item.domain)
        with self._lock: self._put(self._paths, key, item, self.max_items)
        return item

    def save_curriculum(self, item: CurriculumVersion) -> CurriculumVersion:
        key = (item.domain, item.version)
        with self._lock: self._put(self._curricula, key, item, self.max_items)
        return item

    def add_assessment(self, item: Assessment) -> Assessment:
        with self._lock:
            self._assessments.append(item)
            if len(self._assessments) > self.max_items: del self._assessments[:-self.max_items]
        return item

    def skills(self, domain: str) -> tuple[Skill, ...]:
        with self._lock: return tuple(x for x in self._skills.values() if x.domain == domain)

    def lessons(self, domain: str) -> tuple[Lesson, ...]:
        with self._lock: return tuple(x for x in self._lessons.values() if x.domain == domain)

    def course(self, course_id: str) -> Course | None:
        with self._lock: return self._courses.get(course_id)

    def curriculum(self, domain: str, version: str) -> CurriculumVersion | None:
        with self._lock: return self._curricula.get((domain, version))

    def progress(self, scope_id: str, learner_id: str, domain: str) -> LearnerProgress | None:
        with self._lock: return self._progress.get((scope_id, learner_id, domain))

    def path(self, scope_id: str, learner_id: str, domain: str) -> LearningPath | None:
        with self._lock: return self._paths.get((scope_id, learner_id, domain))

    def assessments(self, scope_id: str, learner_id: str) -> tuple[Assessment, ...]:
        with self._lock: return tuple(x for x in self._assessments if x.scope_id == scope_id and x.learner_id == learner_id)
