"""Fail-closed distribution policy decisions."""

from .contracts import (
    DestinationKind,
    DistributionDestination,
    PublicationDecision,
    PublicationPolicy,
    PublicationPolicyResult,
)


class DistributionPolicyEngine:
    """Decides whether a candidate may enter the distribution pipeline.

    This layer never grants platform authority. Actual send/join permissions
    remain platform adapters and the Core permission boundary.
    """

    def __init__(self, policy: PublicationPolicy | None = None) -> None:
        self.policy = policy or PublicationPolicy()

    def evaluate(
        self,
        destination: DistributionDestination,
        *,
        value_score: float,
        confidence: float,
        is_reply: bool = False,
        requested_community_participation: bool = False,
    ) -> PublicationPolicyResult:
        if not 0 <= value_score <= 1 or not 0 <= confidence <= 1:
            return PublicationPolicyResult(PublicationDecision.REJECT, "invalid score")
        if confidence < self.policy.min_confidence:
            return PublicationPolicyResult(PublicationDecision.STAY_QUIET, "confidence below threshold")
        if value_score < self.policy.min_value_score:
            return PublicationPolicyResult(PublicationDecision.STAY_QUIET, "value below threshold")
        if is_reply and not self.policy.allow_replies:
            return PublicationPolicyResult(PublicationDecision.REJECT, "replies disabled by policy")
        if not is_reply and not self.policy.allow_proactive_posts:
            return PublicationPolicyResult(PublicationDecision.STAY_QUIET, "proactive posts disabled by policy")
        if requested_community_participation and (
            destination.kind in {DestinationKind.COMMUNITY, DestinationKind.GROUP, DestinationKind.DISCUSSION}
        ) and not self.policy.allow_community_participation:
            return PublicationPolicyResult(PublicationDecision.REJECT, "community participation requires explicit enablement")
        return PublicationPolicyResult(PublicationDecision.SPEAK, "candidate passed distribution policy")
