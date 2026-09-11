"""Channel-specific teaching and mentorship orchestration."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Mapping, Sequence
from .contracts import EducationMode, LearnerProgress, Lesson, SkillLevel

@dataclass(frozen=True)
class TeachingProfile:
    domain: str
    channel_id: str
    teaching_style: str
    practice_style: str
    tone: str = "clear and encouraging"
    response_shape: str = "explain -> example -> practice"
    def __post_init__(self) -> None:
        if not all(isinstance(v, str) and v.strip() for v in (self.domain, self.channel_id, self.teaching_style, self.practice_style, self.tone, self.response_shape)):
            raise ValueError("teaching profile fields are required")

@dataclass(frozen=True)
class TeachingResponse:
    scope_id: str
    learner_id: str
    domain: str
    mode: EducationMode
    lesson_id: str | None
    text: str
    next_action: str

class TeachingEngine:
    """Produces deterministic teaching structure; actual language generation stays provider-controlled."""
    def __init__(self, profiles: Mapping[str, TeachingProfile] | None = None) -> None:
        self._profiles = dict(profiles or {})

    def register_profile(self, profile: TeachingProfile) -> TeachingProfile:
        self._profiles[profile.channel_id] = profile
        return profile

    def profile(self, channel_id: str) -> TeachingProfile | None:
        return self._profiles.get(channel_id)

    def teach(self, scope_id: str, learner_id: str, profile: TeachingProfile, lesson: Lesson, *, mode: EducationMode = EducationMode.COURSE, progress: LearnerProgress | None = None) -> TeachingResponse:
        if not scope_id.strip() or not learner_id.strip(): raise ValueError("scope_id and learner_id are required")
        if lesson.domain != profile.domain: raise ValueError("lesson domain does not match teaching profile")
        completed = set(progress.completed_lessons) if progress else set()
        if lesson.lesson_id in completed: raise ValueError("lesson is already completed")
        level = progress.current_level.value if progress else SkillLevel.BEGINNER.value
        text = f"{lesson.title}\n\n{lesson.content}\n\nLevel: {level}\nStyle: {profile.teaching_style}\nPractice: {profile.practice_style}"
        return TeachingResponse(scope_id, learner_id, lesson.domain, mode, lesson.lesson_id, text, "practice")

    def mentor_prompt(self, profile: TeachingProfile, goal: str, progress: LearnerProgress | None = None) -> str:
        if not goal.strip(): raise ValueError("goal is required")
        level = progress.current_level.value if progress else SkillLevel.BEGINNER.value
        return f"Act as a {profile.tone} mentor for {profile.domain}. Goal: {goal.strip()}. Learner level: {level}. Use {profile.response_shape}."
