"""Commercial policy: truth and usefulness outrank revenue."""
from __future__ import annotations

from .contracts import BusinessOpportunity, CommercialActionRequest, CommercialRisk


class CommercialPolicy:
    """Fail-closed policy for business actions."""

    def opportunity_allowed(self, opportunity: BusinessOpportunity) -> bool:
        return opportunity.confidence >= 0.60 and opportunity.relevance >= 0.60 and opportunity.value_score >= 0.60

    def recommend(self, opportunities: list[BusinessOpportunity]) -> list[BusinessOpportunity]:
        # Revenue is intentionally absent from ranking: commercial incentives
        # must never override evidence, relevance, or usefulness.
        return sorted(
            (item for item in opportunities if self.opportunity_allowed(item)),
            key=lambda item: (item.value_score, item.confidence, item.relevance),
            reverse=True,
        )

    def authorize(self, request: CommercialActionRequest, owner_approved: bool = False) -> bool:
        if request.risk in (CommercialRisk.HIGH, CommercialRisk.CRITICAL):
            return owner_approved
        if request.requires_owner_approval:
            return owner_approved
        return request.risk == CommercialRisk.LOW
