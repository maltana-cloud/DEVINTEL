from datetime import datetime, timezone
import pytest

from devintel.modules.business import (
    BusinessOpportunity, BusinessService, CommercialActionRequest,
    CommercialPolicy, CommercialRisk, ProductOffer, RevenueRecord, RevenueStatus,
)


def opportunity(**kw):
    base = dict(title="Useful tool", need="A real unmet need", evidence_urls=("https://example.com/evidence",), confidence=.9, relevance=.9, value_score=.8)
    base.update(kw)
    return BusinessOpportunity(**base)


def test_low_value_is_silent_and_revenue_independent():
    service = BusinessService()
    assert not service.discover(opportunity(value_score=.2))
    assert service.ranked_opportunities() == []


def test_rank_is_not_based_on_price():
    policy = CommercialPolicy()
    items = [opportunity(title="A", value_score=.8), opportunity(title="B", value_score=.7)]
    assert [x.title for x in policy.recommend(items)] == ["A", "B"]


def test_scope_and_revenue_are_recorded_without_duplicate_transactions():
    service = BusinessService()
    service.create_offer(ProductOffer("opp-1", "Tool", "Useful", 1000, "NGN"))
    record = RevenueRecord("tx-1", "offer-1", 1000, "NGN", RevenueStatus.CONFIRMED, datetime.now(timezone.utc), "test")
    service.record_verified_revenue(record)
    service.record_verified_revenue(record)
    assert len(service.store.revenue()) == 1


def test_high_risk_requires_owner_approval():
    policy = CommercialPolicy()
    req = CommercialActionRequest("enter_agreement", "owner", CommercialRisk.HIGH, "commercial contract")
    assert not policy.authorize(req)
    assert policy.authorize(req, owner_approved=True)


def test_payment_without_provider_fails_closed():
    service = BusinessService()
    offer = ProductOffer("opp-1", "Tool", "Useful", 1000, "USD")
    with pytest.raises(RuntimeError):
        service.checkout(offer)


def test_contract_rejects_missing_evidence():
    with pytest.raises(ValueError):
        opportunity(evidence_urls=())
