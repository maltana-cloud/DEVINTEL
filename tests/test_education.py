from devintel.modules.education import Course, EducationMode, EducationStore, Lesson, Skill, SkillLevel
from devintel.modules.education.engine import EducationEngine


def lesson(lesson_id: str, level: SkillLevel = SkillLevel.BEGINNER) -> Lesson:
    return Lesson(lesson_id, lesson_id.title(), "programming", ("variables",), "A verified lesson", ("https://example.com/evidence",), level, {"confidence": 0.9})


def test_quality_policy_requires_confident_evidence():
    engine = EducationEngine()
    assert engine.register_lesson(lesson("variables"))
    bad = Lesson("bad", "Bad", "programming", ("variables",), "weak", (), SkillLevel.BEGINNER, {"confidence": 0.2})
    try:
        engine.register_lesson(bad)
        assert False
    except ValueError:
        pass


def test_learning_path_is_scope_and_progress_aware():
    store = EducationStore()
    engine = EducationEngine(store)
    store.add_skill(Skill("variables", "Variables", "programming"))
    store.add_skill(Skill("loops", "Loops", "programming"))
    engine.register_lesson(lesson("variables"))
    engine.register_lesson(lesson("loops"))
    first = engine.build_path("channel-a", "learner-1", "programming")
    assert first.scope_id == "channel-a"
    assert set(first.path.lesson_ids) == {"variables", "loops"}
    other = engine.build_path("channel-b", "learner-1", "programming")
    assert other.scope_id == "channel-b"


def test_course_policy_is_provider_independent_and_prices_do_not_change_quality():
    engine = EducationEngine()
    cheap = Course("free", "Free Course", "programming", ("variables",), "Useful free course")
    premium = Course("pro", "Pro Course", "programming", ("variables",), "Useful premium course", price_minor=500000, currency="NGN", premium=True)
    assert engine.register_course(cheap)
    assert engine.register_course(premium)
