"""System #5 Distribution & Community capabilities."""

from .community import CommunityParticipation, ParticipationRequest, ParticipationResult
from .contracts import (
    DestinationKind, DistributionDestination, DistributionMessage, DistributionResult,
    PublicationDecision, PublicationPolicy, PublicationPolicyResult,
)
from .natural import NaturalPublishingDecision, NaturalPublishingEngine, PublishingCandidate
from .policy import DistributionPolicyEngine
from .rate_limit import RateLimiter
from .router import DistributionRouter
from .service import DistributionService, PublishRequest
from .telegram import TelegramAdapter, TelegramUpdate

__all__ = [
    "CommunityParticipation", "ParticipationRequest", "ParticipationResult",
    "DestinationKind", "DistributionDestination", "DistributionMessage", "DistributionResult",
    "PublicationDecision", "PublicationPolicy", "PublicationPolicyResult",
    "NaturalPublishingDecision", "NaturalPublishingEngine", "PublishingCandidate",
    "DistributionPolicyEngine", "RateLimiter", "DistributionRouter", "DistributionService", "PublishRequest",
    "TelegramAdapter", "TelegramUpdate",
]
