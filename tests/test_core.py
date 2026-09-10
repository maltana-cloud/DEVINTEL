from devintel.core.contracts import ActionRequest, ActionRisk, Confidence, IntelligenceItem
from devintel.core.orchestrator import Orchestrator
from devintel.core.permissions import PermissionDenied


def test_orchestrator_allows_low_risk_action():
    request = ActionRequest(action="research", risk=ActionRisk.LOW)
    assert Orchestrator().authorize(request) is True


def test_high_risk_requires_owner_approval():
    request = ActionRequest(action="spend_money", risk=ActionRisk.HIGH)
    try:
        Orchestrator().authorize(request)
    except PermissionDenied:
        return
    raise AssertionError("high-risk action was not blocked")


def test_intelligence_contract_defaults_to_low_confidence():
    item = IntelligenceItem(id="x", title="Example", summary="Example")
    assert item.confidence == Confidence.LOW
