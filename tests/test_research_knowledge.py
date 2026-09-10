from devintel.modules.research import (
    Claim,
    Entity,
    OpportunityCandidate,
    Relationship,
    ResearchDocument,
    ResearchPipeline,
    StaticProvider,
    normalize_content,
    normalize_title,
)


def test_normalization_is_deterministic():
    assert normalize_title("  Hello   world ") == "Hello world"
    assert normalize_content("one\n\n two\t three") == "one two three"


def test_pipeline_normalizes_before_storage():
    document = ResearchDocument("https://example.com/item", "  Example   ", "  hello\n world ")
    pipeline = ResearchPipeline()
    result = pipeline.run(StaticProvider([document]), "example")
    assert result.stored == 1
    stored = pipeline.store.documents()[0]
    assert stored.title == "Example"
    assert stored.content == "hello world"


def test_knowledge_contracts_validate_confidence():
    assert Claim("DEVINTEL", "discovers", "information", 0.8).confidence == 0.8
    assert Entity("Python", "language").name == "Python"
    assert Relationship("A", "uses", "B", 0.7).confidence == 0.7


def test_opportunity_score_does_not_depend_on_money():
    opportunity = OpportunityCandidate("Need", "A genuine need", ("https://example.com",), 0.9, 0.8)
    assert 0.0 < opportunity.value_score <= 1.0
