from devintel.modules.education import Lesson, Skill, SkillLevel
from devintel.modules.specialists.education import EducationSpecialist

class Source:
    def skills(self, domain):
        return [Skill("variables", "Variables", domain)]
    def lessons(self, domain, level, goals):
        return [Lesson("variables", "Variables", domain, ("variables",), "Verified lesson", ("https://example.com/evidence",), level, {"confidence": 0.9})]

def test_education_specialist_builds_scoped_plan():
    result = EducationSpecialist().execute("programming-channel", "learner-1", "programming", Source())
    assert result.scope_id == "programming-channel"
    assert result.plan.path.scope_id == "programming-channel"
    assert result.plan.path.learner_id == "learner-1"
    assert result.plan.path.lesson_ids == ("variables",)

def test_education_specialist_rejects_missing_scope():
    try:
        EducationSpecialist().execute("", "learner-1", "programming", Source())
        assert False
    except ValueError:
        pass
