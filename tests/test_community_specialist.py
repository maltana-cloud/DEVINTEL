from devintel.modules.specialists.community import CommunitySignal, CommunitySpecialist

class FakeCommunitySource:
    def observe_communities(self, query):
        return [
            CommunitySignal("c1", "Useful question", 0.9, 0.8),
            CommunitySignal("c2", "Lower priority", 0.5, 0.7),
        ]

def test_community_specialist_observes_and_prioritizes():
    result = CommunitySpecialist().execute("community:tech", "unanswered developer questions", FakeCommunitySource())
    assert result.scope_id == "community:tech"
    assert result.signals[0].community_id == "c1"

def test_community_specialist_rejects_invalid_inputs():
    specialist = CommunitySpecialist()
    source = FakeCommunitySource()
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

def test_community_provider_failure_is_isolated():
    class Broken:
        def observe_communities(self, query):
            raise RuntimeError("provider down")
    try:
        CommunitySpecialist().execute("scope", "x", Broken())
        assert False
    except RuntimeError as exc:
        assert "isolated" in str(exc).lower()
