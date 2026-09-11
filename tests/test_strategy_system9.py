from datetime import datetime, timezone

import pytest

from devintel.modules.strategy import (
    CostRecord,
    DomainScore,
    InMemoryStrategyStore,
    InvestmentAction,
    StrategyEngine,
    StrategyPolicy,
)


def domain(scope="channel-a", **kwargs):
    values = dict(value=.9, confidence=.9, demand=.9, cost_efficiency=.9, strategic_fit=.9)
    values.update(kwargs)
    return DomainScore(scope, "developers", **values, reason="verified demand")


def test_high_value_reinvestment_requires_owner_approval():
    policy = StrategyPolicy()
    decision = policy.decide(domain())
    assert decision.action == InvestmentAction.EXPAND
    assert decision.requires_owner_approval is True
    assert policy.authorize(decision) is False
    assert policy.authorize(decision, owner_approved=True) is True


def test_low_confidence_does_not_trigger_commitment():
    decision = StrategyPolicy().decide(domain(confidence=.2))
    assert decision.action == InvestmentAction.RESEARCH
    assert decision.requires_owner_approval is False


def test_costs_are_deduplicated_and_bottlenecks_ranked():
    store = InMemoryStrategyStore()
    engine = StrategyEngine(store)
    record = CostRecord("c1", "a", 100, "USD", "hosting", datetime.now(timezone.utc))
    engine.record_cost(record)
    engine.record_cost(record)
    engine.record_cost(CostRecord("c2", "a", 300, "USD", "provider", datetime.now(timezone.utc)))
    assert len(store.costs("a")) == 2
    assert engine.bottlenecks("a") == ["provider", "hosting"]


def test_scope_isolation():
    store = InMemoryStrategyStore()
    engine = StrategyEngine(store)
    engine.evaluate_domain(domain("a"))
    engine.evaluate_domain(domain("b", demand=.1))
    assert len(engine.summary("a").decisions) == 1
    assert len(engine.summary("b").decisions) == 1
    assert engine.summary("a").decisions[0].target == "developers"


def test_invalid_threshold_rejected():
    with pytest.raises(ValueError):
        StrategyPolicy(min_score=2.0)
