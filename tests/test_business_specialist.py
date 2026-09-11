from devintel.modules.business.contracts import BusinessOpportunity
from devintel.modules.specialists.business import BusinessSpecialist

class Source:
    def discover_business_opportunities(self, query):
        return [BusinessOpportunity("Need", query, ("https://example.com/evidence",), 0.9, 0.9, 0.9)]

def test_business_specialist_discovers_and_ranks():
    result = BusinessSpecialist().execute("scope", "missing service", Source())
    assert result.scope_id == "scope"
    assert len(result.opportunities) == 1

def test_business_specialist_rejects_invalid_scope():
    try:
        BusinessSpecialist().execute("", "x", Source())
    except ValueError as exc:
        assert "scope_id" in str(exc)
    else:
        raise AssertionError("expected ValueError")
