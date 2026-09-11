import pytest
from devintel.providers import ProviderRegistry

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
