from devintel.modules.research.opportunities import OpportunityCandidate
from devintel.modules.specialists.opportunity import OpportunitySpecialist

class FakeOpportunitySource:
    def discover_opportunities(self, query):
        return [
            OpportunityCandidate("Useful tool", "Developers need a faster workflow", ("https://example.com/evidence",), 0.9, 0.9),
            OpportunityCandidate("Smaller need", "Users need documentation", (), 0.5, 0.6),
        ]

def test_opportunity_specialist_is_scoped_and_ranks_by_value_not_price():
    result = OpportunitySpecialist().execute("channel:tech", "developer pain points", FakeOpportunitySource())
    assert result.scope_id == "channel:tech"
    assert len(result.candidates) == 2
    assert result.candidates[0].title == "Useful tool"

def test_opportunity_specialist_rejects_invalid_inputs():
    specialist = OpportunitySpecialist()
    source = FakeOpportunitySource()
    for scope, query in (("", "x"), ("scope", "")):
        try:
            specialist.execute(scope, query, source)
            assert False
        except ValueError:
            pass
    try:
        specialist.execute("scope", "x", object())
        assert False
    except TypeError:
        pass

def test_opportunity_provider_failure_is_isolated():
    class Broken:
        def discover_opportunities(self, query):
            raise RuntimeError("provider down")
    specialist = OpportunitySpecialist()
    try:
        specialist.execute("scope", "x", Broken())
        assert False
    except RuntimeError as exc:
        assert "isolated" in str(exc).lower()
