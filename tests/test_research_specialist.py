import pytest

from devintel.modules.research.contracts import ResearchCandidate, ResearchDocument
from devintel.modules.specialists.research import ResearchSpecialist


class FakeSource:
    def discover(self, query):
        return [ResearchCandidate(url="https://example.com/a", title="Example")]

    def ingest(self, candidate):
        return ResearchDocument(url=candidate.url, title=candidate.title, content="useful research")


def test_research_specialist_is_scoped_and_bounded():
    specialist = ResearchSpecialist()
    result = specialist.execute("channel:tech", "python", FakeSource())
    assert result.scope_id == "channel:tech"
    assert result.query == "python"
    assert result.batch.discovered == 1
    assert result.batch.stored == 1


def test_research_specialist_rejects_missing_scope_or_query():
    specialist = ResearchSpecialist()
    source = FakeSource()
    with pytest.raises(ValueError):
        specialist.execute("", "python", source)
    with pytest.raises(ValueError):
        specialist.execute("scope", "", source)
