from __future__ import annotations

import pytest

from devintel.modules.education.integrations import EducationSubsystemIntegration


class Good:
    def learning_context(self, scope_id, learner_id, domain):
        return ["learner wants a project"]

    def learning_needs(self, scope_id, domain):
        return ["missing fundamentals"]

    def apprenticeship_needs(self, scope_id, domain):
        return ["build a small real tool"]

    def learning_signals(self, scope_id, domain):
        return ["learners ask for beginner lessons"]

    def education_needs(self, scope_id, domain):
        return ["job-ready practice"]

    def domain_priorities(self, scope_id, domain):
        return ["practical skills"]

    def channel_context(self, scope_id, domain):
        return ["public programming channel"]

    def education_health(self, scope_id, domain):
        return "healthy"


def test_all_adjacent_systems_feed_scoped_read_only_signals():
    g = Good()
    integration = EducationSubsystemIntegration(
        conversation=g,
        opportunity=g,
        tool_builder=g,
        growth=g,
        business=g,
        strategy=g,
        distribution=g,
        monitoring=g,
    )
    result = integration.collect("channel:python", "programming", learner_id="learner:1")
    assert result.failed_sources == ()
    assert len(result.signals) == 8
    assert {signal.source for signal in result.signals} == {
        "conversation", "opportunity", "tool_builder", "growth",
        "business", "strategy", "distribution", "monitoring",
    }
    assert all(signal.scope_id == "channel:python" for signal in result.signals)
    assert all(signal.domain == "programming" for signal in result.signals)


def test_scope_is_required_and_never_inferred():
    with pytest.raises(ValueError):
        EducationSubsystemIntegration().collect("", "programming")
    with pytest.raises(ValueError):
        EducationSubsystemIntegration().collect("channel:python", "")


def test_provider_failure_isolated_to_one_source():
    class Broken:
        def learning_needs(self, scope_id, domain):
            raise RuntimeError("provider outage")

    class Healthy:
        def learning_signals(self, scope_id, domain):
            return ["keep teaching"]

    result = EducationSubsystemIntegration(opportunity=Broken(), growth=Healthy()).collect("scope:a", "ai")
    assert result.failed_sources == ("opportunity",)
    assert len(result.signals) == 1
    assert result.signals[0].source == "growth"


def test_unknown_adapter_names_fail_closed():
    with pytest.raises(ValueError):
        EducationSubsystemIntegration(payments=object())


def test_adapter_signals_do_not_create_actions_or_authority():
    result = EducationSubsystemIntegration().collect("scope:a", "forex")
    assert result.signals == ()
    assert not hasattr(result, "actions")
    assert not hasattr(result, "permissions")
