from devintel.modules.growth.contracts import AudienceSignal, SignalKind, AwarenessAction
from devintel.modules.specialists.growth import GrowthSpecialist

class Source:
    def discover_signals(self, query):
        return [
            AudienceSignal("s1", "scope", SignalKind.AUDIENCE_NEED, query, ("https://example.com/evidence",), 0.9),
            AudienceSignal("other", "other-scope", SignalKind.AUDIENCE_NEED, query, ("https://example.com/other",), 0.9),
        ]

def test_growth_specialist_scopes_and_plans():
    result = GrowthSpecialist().execute("scope", "missing docs", Source())
    assert result.scope_id == "scope"
    assert len(result.plans) == 1
    assert result.plans[0].action is AwarenessAction.NO_ACTION
    assert "no destination" in result.plans[0].rationale

def test_growth_specialist_rejects_invalid_input():
    try:
        GrowthSpecialist().execute("", "x", Source())
    except ValueError as exc:
        assert "scope_id" in str(exc)
    else:
        raise AssertionError("expected ValueError")
