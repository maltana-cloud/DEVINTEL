import pytest

from devintel.modules.education import EducationMode, Lesson, LearnerProgress, SkillLevel, TeachingEngine, TeachingProfile
from devintel.runtime import DEVINTELRuntime


def test_teaching_profile_is_channel_specific():
    engine = TeachingEngine()
    programming = TeachingProfile("programming", "channel:code", "build-along", "coding challenge")
    forex = TeachingProfile("forex", "channel:forex", "market-scenario", "risk simulation")
    engine.register_profile(programming)
    engine.register_profile(forex)
    assert engine.profile("channel:code").domain == "programming"
    assert engine.profile("channel:forex").practice_style == "risk simulation"


def test_teaching_rejects_cross_domain_lesson():
    engine = TeachingEngine()
    profile = TeachingProfile("programming", "channel:code", "build-along", "coding challenge")
    lesson = Lesson("market", "Market Structure", "forex", ("structure",), "Verified lesson", ("https://example.com/evidence",), SkillLevel.BEGINNER, {"confidence": 0.9})
    with pytest.raises(ValueError):
        engine.teach("channel:code", "learner", profile, lesson)


def test_teaching_uses_scoped_progress_and_returns_next_action():
    engine = TeachingEngine()
    profile = TeachingProfile("programming", "channel:code", "build-along", "coding challenge")
    lesson = Lesson("variables", "Variables", "programming", ("variables",), "Verified lesson", ("https://example.com/evidence",), SkillLevel.BEGINNER, {"confidence": 0.9})
    progress = LearnerProgress("channel:code", "learner", "programming", (), (), SkillLevel.BEGINNER, ("build apps",))
    response = engine.teach("channel:code", "learner", profile, lesson, mode=EducationMode.MENTORSHIP, progress=progress)
    assert response.scope_id == "channel:code"
    assert response.mode is EducationMode.MENTORSHIP
    assert response.next_action == "practice"
    assert "build-along" in response.text


def test_runtime_exposes_teaching_without_authority():
    runtime = DEVINTELRuntime()
    profile = TeachingProfile("programming", "channel:code", "build-along", "coding challenge")
    runtime.register_teaching_profile(profile)
    assert runtime.teaching_profile("channel:code") == profile
    assert not hasattr(runtime.teaching, "execute")
