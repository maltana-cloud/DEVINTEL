import pytest

from devintel.providers import ProviderHealth, ProviderRegistry, ProviderResult


def test_provider_registry_is_bounded_and_replaceable():
    registry = ProviderRegistry(max_providers=1)
    registry.register("a", object())
    registry.register("a", object())
    with pytest.raises(RuntimeError):
        registry.register("b", object())
    assert registry.ids() == ("a",)


def test_provider_registry_missing_provider_is_safe():
    registry = ProviderRegistry()
    assert registry.get("missing") is None
    assert registry.remove("missing") is False


def test_provider_health_defaults_metadata_without_shared_state():
    first = ProviderHealth(provider_id="x", healthy=True)
    second = ProviderHealth(provider_id="y", healthy=True)
    assert first.metadata == {}
    assert second.metadata == {}
    assert first.metadata is not second.metadata


def test_provider_contracts_validate_identity_and_result_consistency():
    with pytest.raises(ValueError):
        ProviderHealth(provider_id="", healthy=True)
    with pytest.raises(ValueError):
        ProviderResult(provider_id="", success=True)
    with pytest.raises(ValueError):
        ProviderResult(provider_id="x", success=True, error="unexpected")


def test_provider_result_can_represent_failure_safely():
    result = ProviderResult(provider_id="x", success=False, error="temporarily unavailable")
    assert result.success is False
    assert result.error == "temporarily unavailable"
