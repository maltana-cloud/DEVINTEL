"""Learning outcome measurement and safe feedback signals."""
from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
from .contracts import Assessment, AssessmentResult, SkillLevel

@dataclass(frozen=True)
class LearningOutcome:
    scope_id: str
    learner_id: str
    domain: str
    task_id: str
    score: float
    result: AssessmentResult
    feedback: str
    observed_at: datetime
    def __post_init__(self) -> None:
        if not all(isinstance(v, str) and v.strip() for v in (self.scope_id, self.learner_id, self.domain, self.task_id, self.feedback)):
            raise ValueError("outcome identifiers and feedback are required")
        if not 0.0 <= self.score <= 1.0: raise ValueError("score must be between 0 and 1")
        if self.observed_at.tzinfo is None: raise ValueError("observed_at must be timezone-aware")

@dataclass(frozen=True)
class OutcomeSummary:
    scope_id: str
    learner_id: str
    domain: str
    attempts: int
    average_score: float
    passed: int
    needs_practice: int
    failed: int
    recommended_level: SkillLevel

class OutcomeEngine:
    """Bounded, scope-isolated measurement; recommendations never grant authority."""
    def __init__(self, max_outcomes: int = 10000) -> None:
        if max_outcomes < 1: raise ValueError("max_outcomes must be positive")
        self.max_outcomes = max_outcomes
        self._outcomes: list[LearningOutcome] = []

    def record(self, assessment: Assessment) -> LearningOutcome:
        if not assessment.domain: raise ValueError("assessment domain is required")
        outcome = LearningOutcome(assessment.scope_id, assessment.learner_id, assessment.domain, assessment.task_id, assessment.score, assessment.result, assessment.feedback, assessment.assessed_at)
        self._outcomes.append(outcome)
        if len(self._outcomes) > self.max_outcomes: del self._outcomes[:-self.max_outcomes]
        return outcome

    def outcomes(self, scope_id: str, learner_id: str, domain: str) -> tuple[LearningOutcome, ...]:
        return tuple(x for x in self._outcomes if x.scope_id == scope_id and x.learner_id == learner_id and x.domain == domain)

    def summary(self, scope_id: str, learner_id: str, domain: str) -> OutcomeSummary:
        items = self.outcomes(scope_id, learner_id, domain)
        if not items: return OutcomeSummary(scope_id, learner_id, domain, 0, 0.0, 0, 0, 0, SkillLevel.BEGINNER)
        average = sum(x.score for x in items) / len(items)
        passed = sum(x.result is AssessmentResult.PASS for x in items)
        practice = sum(x.result is AssessmentResult.NEEDS_PRACTICE for x in items)
        failed = sum(x.result is AssessmentResult.FAIL for x in items)
        level = SkillLevel.ADVANCED if average >= 0.85 and passed / len(items) >= 0.8 else SkillLevel.INTERMEDIATE if average >= 0.65 else SkillLevel.BEGINNER
        return OutcomeSummary(scope_id, learner_id, domain, len(items), round(average, 6), passed, practice, failed, level)

class EducationFeedbackBridge:
    """Turns education outcomes into read-only autonomy observations."""
    def __init__(self, outcomes: OutcomeEngine) -> None: self.outcomes = outcomes

    def observe(self, scope_id: str):
        from ...autonomy.contracts import Observation
        return tuple(Observation(scope_id, "education.outcome", x) for x in self.outcomes._outcomes if x.scope_id == scope_id)

    def recommend(self, scope_id: str, learner_id: str, domain: str) -> dict[str, object]:
        summary = self.outcomes.summary(scope_id, learner_id, domain)
        return {"scope_id": scope_id, "learner_id": learner_id, "domain": domain, "recommended_level": summary.recommended_level.value, "average_score": summary.average_score, "attempts": summary.attempts}
