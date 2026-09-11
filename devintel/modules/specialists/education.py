"""Education and mentorship specialist behind DEVINTEL's plugin boundary."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Protocol, Sequence
from ..education.contracts import Lesson, Skill, SkillLevel
from ..education.engine import EducationEngine, EducationPlan
from ..plugins.contracts import PluginAction, PluginManifest, PluginRisk
from ..plugins.service import PluginService

@dataclass(frozen=True)
class EducationSpecialistResult:
    scope_id: str
    plan: EducationPlan

class EducationSource(Protocol):
    def lessons(self, domain: str, level: SkillLevel, goals: Sequence[str]) -> Sequence[Lesson]: ...
    def skills(self, domain: str) -> Sequence[Skill]: ...

class EducationSpecialist:
    plugin_id = "specialist.education"
    def __init__(self, plugins: PluginService | None = None, engine: EducationEngine | None = None) -> None:
        self.plugins = plugins or PluginService()
        self.engine = engine or EducationEngine()
        self.plugins.register(PluginManifest(
            self.plugin_id, "Education Specialist", "1.0.0",
            "Builds scoped learning paths and mentorship-ready education plans without granting authority.",
            ("education.plan", "education.mentor"), ("education.read",), PluginRisk.LOW,
        ))
        self.attach()

    def execute(self, scope_id: str, learner_id: str, domain: str, source: EducationSource, *, level: SkillLevel = SkillLevel.BEGINNER, goals: Sequence[str] = ()) -> EducationSpecialistResult:
        scope = scope_id.strip() if isinstance(scope_id, str) else ""
        learner = learner_id.strip() if isinstance(learner_id, str) else ""
        subject = domain.strip() if isinstance(domain, str) else ""
        if not scope or not learner or not subject: raise ValueError("scope_id, learner_id, and domain are required")
        if not hasattr(source, "lessons") or not hasattr(source, "skills"): raise TypeError("source must implement education discovery")
        action = PluginAction(self.plugin_id, "education.plan", scope, PluginRisk.LOW, "bounded education planning", payload={"learner_id": learner, "domain": subject, "source": source, "level": level, "goals": tuple(goals)})
        result = self.plugins.execute(action)
        if not result.success: raise RuntimeError(result.error)
        return result.output

    def attach(self) -> None:
        def run(action: PluginAction) -> EducationSpecialistResult:
            payload = action.payload
            if not isinstance(payload, dict): raise TypeError("education action payload must be a mapping")
            source, learner, domain, level, goals = payload.get("source"), payload.get("learner_id"), payload.get("domain"), payload.get("level"), payload.get("goals", ())
            if not hasattr(source, "lessons") or not hasattr(source, "skills"): raise TypeError("education source is invalid")
            for skill in source.skills(domain):
                if not isinstance(skill, Skill): raise TypeError("education source returned invalid skill")
                self.engine.store.add_skill(skill)
            for lesson in source.lessons(domain, level, goals):
                if not isinstance(lesson, Lesson): raise TypeError("education source returned invalid lesson")
                self.engine.register_lesson(lesson)
            plan = self.engine.build_path(action.scope_id, learner, domain, goals=goals, level=level)
            return EducationSpecialistResult(action.scope_id, plan)
        self.plugins.attach(self.plugin_id, run)
