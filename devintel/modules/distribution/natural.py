"""Natural, value-first publishing decisions."""

from dataclasses import dataclass
from enum import Enum

from .contracts import PublicationDecision


class PublishingPressure(str, Enum):
    NONE = "none"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass(frozen=True)
class PublishingCandidate:
    value_score: float
    confidence: float
    freshness: float = 0.0
    urgency: float = 0.0
    duplicate: bool = False
    already_covered: bool = False

    def __post_init__(self) -> None:
        for name in ("value_score", "confidence", "freshness", "urgency"):
            value = getattr(self, name)
            if not 0.0 <= value <= 1.0:
                raise ValueError(f"{name} must be between 0 and 1")


@dataclass(frozen=True)
class NaturalPublishingDecision:
    decision: PublicationDecision
    score: float
    reason: str


class NaturalPublishingEngine:
    """Prefers silence over low-value or repetitive speech."""

    def decide(self, candidate: PublishingCandidate) -> NaturalPublishingDecision:
        if candidate.duplicate or candidate.already_covered:
            return NaturalPublishingDecision(PublicationDecision.STAY_QUIET, 0.0, "duplicate or already covered")
        score = round(
            candidate.value_score * 0.45
            + candidate.confidence * 0.30
            + candidate.freshness * 0.15
            + candidate.urgency * 0.10,
            4,
        )
        if candidate.confidence < 0.60:
            return NaturalPublishingDecision(PublicationDecision.STAY_QUIET, score, "confidence is insufficient")
        if score >= 0.65:
            return NaturalPublishingDecision(PublicationDecision.SPEAK, score, "useful information warrants publication")
        if score >= 0.50:
            return NaturalPublishingDecision(PublicationDecision.DEFER, score, "candidate may become useful with more evidence or context")
        return NaturalPublishingDecision(PublicationDecision.STAY_QUIET, score, "no sufficient value to interrupt the audience")
