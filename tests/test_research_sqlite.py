from devintel.modules.research import ResearchDocument, ResearchObservation, SQLiteResearchStore


def test_sqlite_store_persists_documents_and_observations(tmp_path):
    path = str(tmp_path / "research.db")
    store = SQLiteResearchStore(path)
    document = ResearchDocument(
        "https://example.com/item#fragment",
        "Example",
        "content",
        publisher="Example Press",
        metadata={"topic": "python"},
    )
    assert store.add_document(document)
    store.add_observation(
        ResearchObservation(
            document.url,
            "fact",
            "Python is useful",
            confidence=0.8,
            evidence=(document.url,),
            metadata={"source": "document"},
        )
    )
    store.close()

    reopened = SQLiteResearchStore(path)
    loaded = reopened.get("https://example.com/item")
    assert loaded is not None
    assert loaded.title == "Example"
    assert loaded.publisher == "Example Press"
    assert loaded.metadata == {"topic": "python"}
    assert reopened.count_documents() == 1
    assert reopened.count_observations() == 1
    observation = reopened.observations()[0]
    assert observation.confidence == 0.8
    assert observation.evidence == ("https://example.com/item",)
    assert observation.metadata == {"source": "document"}
    reopened.close()


def test_sqlite_store_rejects_url_and_content_duplicates(tmp_path):
    store = SQLiteResearchStore(str(tmp_path / "research.db"))
    first = ResearchDocument("https://example.com/a", "A", "same")
    same_url = ResearchDocument("https://example.com/a#fragment", "B", "different")
    same_content = ResearchDocument("https://example.com/b", "B", "same")
    assert store.add_document(first)
    assert not store.add_document(same_url)
    assert not store.add_document(same_content)
    assert store.count_documents() == 1
    store.close()
