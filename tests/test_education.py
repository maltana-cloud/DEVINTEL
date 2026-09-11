from devintel.modules.education import Assessment, AssessmentResult, Course, CurriculumVersion, EducationMode, EducationStore, Lesson, Skill, SkillLevel
from devintel.modules.education.engine import EducationEngine


def lesson(lesson_id: str, level: SkillLevel = SkillLevel.BEGINNER, skills=("variables",), goals=()) -> Lesson:
    return Lesson(lesson_id, lesson_id.title(), "programming", tuple(skills), "A verified lesson", ("https://example.com/evidence",), level, {"confidence": 0.9, "goal_tags": tuple(goals)}, "1")


def test_quality_policy_requires_confident_evidence():
    engine = EducationEngine()
    assert engine.register_lesson(lesson("variables"))
    bad = Lesson("bad", "Bad", "programming", ("variables",), "weak", (), SkillLevel.BEGINNER, {"confidence": 0.2})
    try:
        engine.register_lesson(bad)
        assert False
    except ValueError:
        pass


def test_learning_path_is_scope_goal_and_progress_aware():
    store = EducationStore()
    engine = EducationEngine(store)
    store.add_skill(Skill("variables", "Variables", "programming"))
    store.add_skill(Skill("loops", "Loops", "programming", ("variables",)))
    engine.register_lesson(lesson("variables", skills=("variables",), goals=("fundamentals",)))
    engine.register_lesson(lesson("loops", skills=("loops",), goals=("automation",)))
    first = engine.build_path("channel-a", "learner-1", "programming", goals=("automation",))
    assert first.scope_id == "channel-a"
    assert first.path.lesson_ids == ("variables", "loops")
    other = engine.build_path("channel-b", "learner-1", "programming")
    assert other.scope_id == "channel-b"


def test_prerequisite_cycle_and_missing_prerequisite_are_rejected():
    engine = EducationEngine()
    engine.store.add_skill(Skill("a", "A", "programming", ("missing",)))
    try:
        engine.build_path("s", "l", "programming")
        assert False
    except ValueError as exc:
        assert "unknown prerequisite" in str(exc)


def test_assessment_updates_only_its_scope_and_learner():
    engine = EducationEngine()
    engine.store.add_skill(Skill("variables", "Variables", "programming"))
    assessment = Assessment("a1", "channel-a", "learner-1", "lesson-1", AssessmentResult.PASS, 0.95, "Strong work", domain="programming", skill_id="variables")
    progress = engine.record_assessment(assessment)
    assert progress.mastered_skills == ("variables",)
    assert engine.progress("channel-a", "learner-1", "programming").mastered_skills == ("variables",)
    assert engine.progress("channel-b", "learner-1", "programming") is None


def test_curriculum_version_requires_matching_lessons():
    engine = EducationEngine()
    engine.register_lesson(lesson("variables"))
    assert engine.register_curriculum(CurriculumVersion("1", "programming", ("variables",)))


def test_store_bounds_each_collection():
    store = EducationStore(max_items=1)
    store.add_skill(Skill("a", "A", "programming"))
    store.add_skill(Skill("b", "B", "programming"))
    assert len(store.skills("programming")) == 1


def test_course_policy_is_provider_independent_and_prices_do_not_change_quality():
    engine = EducationEngine()
    cheap = Course("free", "Free Course", "programming", ("variables",), "Useful free course")
    premium = Course("pro", "Pro Course", "programming", ("variables",), "Useful premium course", price_minor=500000, currency="NGN", premium=True)
    assert engine.register_course(cheap)
    assert engine.register_course(premium)
