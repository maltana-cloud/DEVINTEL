from devintel.modules.research import ResearchCandidate, ResearchDocument, ResearchPipeline, InMemoryResearchStore
from devintel.modules.research.limits import ResearchLimits


class BoundedProvider:
    def discover(self, query):
        return [ResearchCandidate("https://example.com/1"), ResearchCandidate("https://example.com/2")]

    def ingest(self, candidate):
        return ResearchDocument(candidate.url, "Example", "content")


def test_pipeline_enforces_candidate_limit():
    class Provider(BoundedProvider):
        def discover(self, query):
            return [ResearchCandidate(f"https://example.com/{i}") for i in range(5)]

    result = ResearchPipeline(limits=ResearchLimits(max_candidates=2)).run(Provider(), "query")
    assert result.discovered == 2
    assert result.stored == 2


def test_pipeline_rejects_oversized_document():
    class Provider(BoundedProvider):
        def ingest(self, candidate):
            return ResearchDocument(candidate.url, "Example", "x" * 20)

    result = ResearchPipeline(limits=ResearchLimits(max_document_chars=10)).run(Provider(), "query")
    assert result.ingested == 0
    assert result.invalid_candidates == 1


def test_pipeline_isolates_repeated_provider_failures():
    class Provider(BoundedProvider):
        def discover(self, query):
            return [ResearchCandidate(f"https://example.com/{i}") for i in range(10)]

        def ingest(self, candidate):
            raise RuntimeError("provider failure")

    result = ResearchPipeline(limits=ResearchLimits(max_provider_failures=3)).run(Provider(), "query")
    assert result.ingested == 0
    assert result.provider_failures == 3


def test_store_counts_are_thread_safe_views():
    store = InMemoryResearchStore()
    store.add_document(ResearchDocument("https://example.com", "Example", "content"))
    assert store.count_documents() == 1
    assert store.count_observations() == 0
