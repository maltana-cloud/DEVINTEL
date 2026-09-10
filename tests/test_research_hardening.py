from devintel.modules.research import (
    InMemoryResearchStore,
    ProvenanceVerifier,
    ResearchCandidate,
    ResearchDocument,
    ResearchPipeline,
    ResearchObservation,
    SQLiteResearchStore,
)
from devintel.modules.research.limits import ResearchLimits


class BoundedProvider:
    def discover(self, query):
        return [ResearchCandidate("https://example.com/1"), ResearchCandidate("https://example.com/2")]

    def ingest(self, candidate):
        return ResearchDocument(candidate.url, "Example", f"content from {candidate.url}")


def test_pipeline_enforces_candidate_limit():
    class Provider(BoundedProvider):
        def discover(self, query):
            return [ResearchCandidate(f"https://example.com/{i}") for i in range(5)]

    result = ResearchPipeline(limits=ResearchLimits(max_candidates=2)).run(Provider(), "query")
    assert result.discovered == 2
    assert result.stored == 2


def test_pipeline_rejects_oversized_document():
    class Provider(BoundedProvider):
        def discover(self, query):
            return [ResearchCandidate("https://example.com/1")]

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


def test_provenance_verifier_is_conservative():
    document = ResearchDocument("https://example.com/a", "Example", "content", publisher="Example")
    observation = ResearchObservation(document.url, "fact", "content", 0.9, (document.url,))
    result = ProvenanceVerifier().verify(document, observation)
    assert result.verified is True
    assert result.confidence == 0.9


def test_provenance_verifier_rejects_missing_evidence():
    document = ResearchDocument("https://example.com/a", "Example", "content", publisher="Example")
    observation = ResearchObservation(document.url, "fact", "content", 0.9)
    result = ProvenanceVerifier().verify(document, observation)
    assert result.verified is False
    assert result.confidence < 0.9


def test_sqlite_store_persists_documents_and_observations(tmp_path):
    path = str(tmp_path / "research.sqlite3")
    store = SQLiteResearchStore(path)
    document = ResearchDocument(
        "https://example.com/a", "Example", "content", publisher="Example",
        metadata={"domain": "test"},
    )
    assert store.add_document(document) is True
    assert store.add_document(document) is False
    store.add_observation(ResearchObservation(document.url, "fact", "content", 0.8, (document.url,)))
    store.close()

    reopened = SQLiteResearchStore(path)
    assert reopened.count_documents() == 1
    assert reopened.get(document.url).metadata == {"domain": "test"}
    assert reopened.count_observations() == 1
    reopened.close()
