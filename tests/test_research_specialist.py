import pytest

from devintel.modules.research.contracts import ResearchCandidate, ResearchDocument
from devintel.modules.specialists.research import ResearchSpecialist


class FakeSource:
    def discover(self, query):
        return [ResearchCandidate(url="https://example.com/a", title="Example")]

    def ingest(self, candidate):
        return ResearchDocument(url=candidate.url, title=candidate.title, content="useful research")


class FailingSource(FakeSource):
    def discover(self, query):
        raise RuntimeError("provider unavailable")


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


def test_research_specialist_rejects_invalid_provider():
    with pytest.raises(TypeError):
        ResearchSpecialist().execute("scope", "python", object())


def test_research_failure_isolated_at_plugin_boundary():
    specialist = ResearchSpecialist()
    with pytest.raises(RuntimeError, match="plugin isolated"):
        specialist.execute("channel:tech", "python", FailingSource())
