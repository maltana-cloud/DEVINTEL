from devintel.modules.specialists.truth import TruthSpecialist

class Source:
    def evidence_urls(self, claim):
        return ["https://example.com/evidence"]
    def source_confidences(self, claim):
        return [0.9, 0.8]
    def contradictory(self, claim):
        return False

def test_truth_specialist_assesses_verified_claim():
    result = TruthSpecialist().execute("channel:tech", "A factual claim", Source())
    assert result.scope_id == "channel:tech"
    assert result.assessment.verified is True
    assert result.assessment.confidence == 0.8

def test_truth_specialist_preserves_contradiction():
    class Conflicting(Source):
        def contradictory(self, claim):
            return True
    result = TruthSpecialist().execute("channel:tech", "A disputed claim", Conflicting())
    assert result.assessment.verified is False
    assert result.assessment.contradiction is True
    assert result.assessment.confidence <= 0.49

def test_truth_specialist_rejects_invalid_inputs():
    specialist = TruthSpecialist()
    for scope, claim in (("", "claim"), ("scope", "")):
        try:
            specialist.execute(scope, claim, Source())
            assert False
        except ValueError:
            pass
    try:
        specialist.execute("scope", "claim", object())
        assert False
    except TypeError:
        pass

def test_truth_provider_failure_is_isolated():
    class Broken(Source):
        def evidence_urls(self, claim):
            raise RuntimeError("provider down")
    try:
        TruthSpecialist().execute("scope", "claim", Broken())
        assert False
    except RuntimeError as exc:
        assert "isolated" in str(exc).lower()
