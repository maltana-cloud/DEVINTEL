"""Natural, value-driven publishing decisions.

A schedule may wake the system up, but it never forces a post. The decision is
based on usefulness, relevance, importance, freshness, confidence, and recent
publishing pressure. Domain/channel-specific policy is supplied by callers.
"""

from __future__ import annotations

from dataclasses import dataclass

from core.contracts import IntelligenceItem, PublishDecision


@dataclass(frozen=True)
class FeedPolicy:
    minimum_score: float = 0.68
    minimum_confidence: float = 0.70
    maximum_uncertainty: float = 0.30
    recent_post_pressure: float = 0.0
    pressure_weight: float = 0.20


def score_item(item: IntelligenceItem, policy: FeedPolicy = FeedPolicy()) -> float:
    """Calculate a deterministic first-pass value score in [0, 1]."""
    base = (
        0.25 * item.relevance
        + 0.25 * item.importance
        + 0.20 * item.freshness
        + 0.30 * (1.0 - item.uncertainty)
    )
    score = base - policy.pressure_weight * policy.recent_post_pressure
    return max(0.0, min(1.0, score))


def decide(item: IntelligenceItem, policy: FeedPolicy = FeedPolicy()) -> PublishDecision:
    """Decide whether an item earns a natural publication opportunity."""
    confidence = max((p.confidence for p in item.provenance), default=0.0)
    score = score_item(item, policy)

    if not item.provenance:
        return PublishDecision(False, "no provenance", score)
    if confidence < policy.minimum_confidence:
        return PublishDecision(False, "confidence below policy threshold", score)
    if item.uncertainty > policy.maximum_uncertainty:
        return PublishDecision(False, "uncertainty above policy threshold", score)
    if score < policy.minimum_score:
        return PublishDecision(False, "insufficient value for publication", score)

    return PublishDecision(True, "item earns a natural publication opportunity", score)
