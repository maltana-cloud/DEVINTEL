from devintel.modules.research.contracts import ResearchCandidate, ResearchDocument
from devintel.modules.specialists.research import ResearchSpecialist


class FakeSource:
    def discover(self, query):
        return [ResearchCandidate(url="https://example.com/a", title="Example", source="example")]

    def ingest(self, candidate):
        return ResearchDocument(url=candidate.url, title=candidate.title, content="useful research")


def test_research_specialist_is_scoped_and_bounded():
    specialist = ResearchSpecialist()
    specialist.attach()
    result = specialist.execute("channel:tech", "python", FakeSource())
    assert result.scope_id == "channel:tech"
    assert result.query == "python"
    assert result.batch.discovered == 1
    assert result.batch.stored == 1


def test_research_specialist_rejects_missing_scope_or_query():
    specialist = ResearchSpecialist()
    specialist.attach()
    source = FakeSource()
    try:
        specialist.execute("", "python", source)
        assert False
    except ValueError:
        pass
    try:
        specialist.execute("scope", "", source)
        assert False
    except ValueError:
        pass
