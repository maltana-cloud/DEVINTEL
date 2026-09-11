"""Provider adapter boundaries for replaceable external integrations."""
from .contracts import ProviderCapability, ProviderHealth, ProviderResult
from .registry import ProviderRegistry

__all__ = ["ProviderCapability", "ProviderHealth", "ProviderResult", "ProviderRegistry"]
