from devintel.modules.research import (
    InMemoryResearchStore,
    ResearchCandidate,
    ResearchDocument,
    ResearchPipeline,
    ResearchObservation,
)


class Provider:
    def __init__(self):
        self.failed = False

    def discover(self, query):
        return [
            ResearchCandidate("HTTPS://Example.com/article/#section", title="Example"),
            ResearchCandidate("https://example.com/article/", title="Duplicate"),
        ]

    def ingest(self, candidate):
        return ResearchDocument(candidate.url, candidate.title or "Example", "hello world", "Example")


def test_url_is_canonicalized_and_fragment_removed():
    candidate = ResearchCandidate("HTTPS://Example.com/a/#x")
    assert candidate.url == "https://example.com/a"


def test_document_content_hash_is_stable():
    a = ResearchDocument("https://example.com/a", "A", "same")
    b = ResearchDocument("https://example.com/b", "B", "same")
    assert a.content_hash == b.content_hash


def test_store_deduplicates_by_url_and_content():
    store = InMemoryResearchStore()
    a = ResearchDocument("https://example.com/a", "A", "same")
    b = ResearchDocument("https://example.com/a", "A2", "different")
    c = ResearchDocument("https://example.com/c", "C", "same")
    assert store.add_document(a) is True
    assert store.add_document(b) is False
    assert store.add_document(c) is False
    assert len(store.documents()) == 1


def test_pipeline_isolates_bad_provider_item_and_counts_duplicates():
    result = ResearchPipeline().run(Provider(), "python")
    assert result.discovered == 2
    assert result.ingested == 2
    assert result.stored == 1
    assert result.duplicates == 1


def test_observation_requires_bounded_confidence():
    try:
        ResearchObservation("https://example.com", "fact", "x", 1.1)
    except ValueError:
        return
    raise AssertionError("out-of-range confidence was accepted")
