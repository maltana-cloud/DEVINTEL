from devintel.modules.specialists.strategy import StrategySpecialist
from devintel.modules.strategy.contracts import DomainScore, InvestmentAction

class Source:
    def discover_domains(self, query):
        return [
            DomainScore("scope", "docs", 0.9, 0.9, 0.8, 0.8, 0.9, query),
            DomainScore("other", "other", 0.9, 0.9, 0.9, 0.9, 0.9, query),
        ]

def test_strategy_specialist_scopes_and_recommends():
    result = StrategySpecialist().execute("scope", "missing docs", Source())
    assert result.scope_id == "scope"
    assert len(result.decisions) == 1
    assert result.decisions[0].action in set(InvestmentAction)

def test_strategy_specialist_rejects_invalid_scope():
    try:
        StrategySpecialist().execute("", "x", Source())
    except ValueError as exc:
        assert "scope_id" in str(exc)
    else:
        raise AssertionError("expected ValueError")
