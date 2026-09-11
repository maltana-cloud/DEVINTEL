"""Fail-closed growth decision policy."""
from .contracts import AudienceSignal, AwarenessAction, GrowthScore

class GrowthPolicy:
    def __init__(self, min_confidence: float = 0.60, min_value: float = 0.55) -> None:
        if not 0 <= min_confidence <= 1 or not 0 <= min_value <= 1: raise ValueError("thresholds must be between 0 and 1")
        self.min_confidence = min_confidence; self.min_value = min_value
    def score(self, signal: AudienceSignal) -> GrowthScore:
        evidence = min(1.0, len(signal.evidence_urls) / 3.0)
        freshness = 1.0 if signal.observed_at is not None else 0.0
        value = min(1.0, 0.55 * signal.confidence + 0.30 * evidence + 0.15 * freshness)
        return GrowthScore(value=value, confidence=signal.confidence, reasons=(f"confidence={signal.confidence:.2f}", f"evidence={len(signal.evidence_urls)}"))
    def choose(self, signal: AudienceSignal, score: GrowthScore) -> AwarenessAction:
        if score.confidence < self.min_confidence or score.value < self.min_value: return AwarenessAction.NO_ACTION
        if signal.kind.value in {"audience_need", "unanswered_question", "feedback"}: return AwarenessAction.EDUCATE
        if signal.kind.value == "partnership": return AwarenessAction.PARTNER
        if signal.kind.value == "distribution": return AwarenessAction.DISTRIBUTE
        return AwarenessAction.RESEARCH
