"""Knowledge and research primitives for DEVINTEL."""

from .contracts import ResearchCandidate, ResearchDocument, ResearchObservation, canonicalize_url, content_digest
from .knowledge import Claim, Entity, Relationship
from .limits import ResearchLimits
from .normalization import normalize_content, normalize_text, normalize_title
from .opportunities import OpportunityCandidate
from .pipeline import ResearchBatch, ResearchPipeline, SourceProvider
from .providers import RSSProvider, StaticProvider
from .store import InMemoryResearchStore

__all__ = [
    "ResearchCandidate", "ResearchDocument", "ResearchObservation", "canonicalize_url", "content_digest",
    "Claim", "Entity", "Relationship", "ResearchLimits",
    "normalize_content", "normalize_text", "normalize_title", "OpportunityCandidate",
    "ResearchBatch", "ResearchPipeline", "SourceProvider", "RSSProvider", "StaticProvider",
    "InMemoryResearchStore",
]
