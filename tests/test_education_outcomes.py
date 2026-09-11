from devintel.modules.education import Assessment, AssessmentResult, SkillLevel
from devintel.modules.education.outcomes import OutcomeEngine
from devintel.runtime import DEVINTELRuntime


def assessment(scope, score, result=AssessmentResult.PASS):
    return Assessment(f"a-{scope}-{score}", scope, "learner", "task", result, score, "feedback", domain="programming", skill_id="variables")


def test_outcome_summary_is_scoped_and_adaptive():
    outcomes = OutcomeEngine()
    outcomes.record(assessment("channel:a", 0.95))
    outcomes.record(assessment("channel:a", 0.9))
    outcomes.record(assessment("channel:b", 0.2, AssessmentResult.FAIL))
    high = outcomes.summary("channel:a", "learner", "programming")
    low = outcomes.summary("channel:b", "learner", "programming")
    assert high.attempts == 2
    assert high.recommended_level is SkillLevel.ADVANCED
    assert low.attempts == 1
    assert low.recommended_level is SkillLevel.BEGINNER


def test_runtime_records_assessment_through_core_and_updates_outcomes():
    runtime = DEVINTELRuntime()
    result = runtime.record_education_assessment(assessment("channel:a", 0.9))
    assert result.success is True
    summary = runtime.education_outcome_summary("channel:a", "learner", "programming")
    assert summary.attempts == 1
    assert summary.average_score == 0.9


def test_runtime_education_feedback_observer_cannot_cross_scope():
    runtime = DEVINTELRuntime()
    runtime.record_education_assessment(assessment("channel:a", 0.9))
    assert all(item.scope_id == "channel:a" for item in runtime.education_feedback_observer("channel:a"))
    assert runtime.education_feedback_observer("channel:b") == ()
