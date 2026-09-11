from devintel.modules.education.adapters import TruthCheckedEducationProvider
from devintel.modules.education.contracts import Lesson, Skill, SkillLevel


class Source:
    def skills(self, domain):
        return [Skill("skill", "Skill", domain)]

    def lessons(self, domain, level, goals):
        return [
            Lesson("good", "Good", domain, ("skill",), "verified", ("https://example.com/good",), level, {"confidence": 0.9}),
            Lesson("weak", "Weak", domain, ("skill",), "weak", ("https://example.com/weak",), level, {"confidence": 0.2}),
            Lesson("none", "None", domain, ("skill",), "unproven", (), level, {"confidence": 0.9}),
        ]


class Truth:
    def assess(self, claim, evidence_urls, source_confidences, contradictory=False):
        from devintel.modules.security.truth import ClaimAssessment
        confidence = min(source_confidences)
        return ClaimAssessment(confidence >= 0.6, confidence, evidence_urls=tuple(evidence_urls), contradiction=contradictory)


def test_truth_checked_provider_filters_weak_and_unproven_lessons():
    provider = TruthCheckedEducationProvider(Source(), Truth())
    lessons = provider.lessons("programming", SkillLevel.BEGINNER, ())
    assert tuple(x.lesson_id for x in lessons) == ("good",)
    assert lessons[0].metadata["truth_confidence"] == 0.9
