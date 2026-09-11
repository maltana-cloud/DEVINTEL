"""Provider adapter boundaries for replaceable external integrations."""
from .contracts import ProviderCapability, ProviderHealth, ProviderResult
from .live import (
    GenerationProvider,
    GenerationRequest,
    GenerationResponse,
    ProviderRouter,
    ResearchProvider,
    ResearchRequest,
    ResearchResult,
)
from .registry import ProviderRegistry

__all__ = [
    "ProviderCapability",
    "ProviderHealth",
    "ProviderResult",
    "ProviderRegistry",
    "GenerationProvider",
    "GenerationRequest",
    "GenerationResponse",
    "ResearchProvider",
    "ResearchRequest",
    "ResearchResult",
    "ProviderRouter",
]
