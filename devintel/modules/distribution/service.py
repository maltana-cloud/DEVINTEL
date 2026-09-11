"""End-to-end distribution orchestration with bounded authority."""

from dataclasses import dataclass

from devintel.core.audit import AuditLog, AuditRecord
from devintel.core.contracts import ActionRequest, ActionRisk
from devintel.core.events import EventBus, RuntimeEvent
from devintel.core.permissions import PermissionDenied, PermissionPolicy

from .contracts import DistributionDestination, DistributionMessage, DistributionResult, PublicationDecision
from .natural import NaturalPublishingEngine, PublishingCandidate
from .policy import DistributionPolicyEngine
from .rate_limit import RateLimiter
from .router import DistributionRouter


@dataclass(frozen=True)
class PublishRequest:
    destination: DistributionDestination
    message: DistributionMessage
    value_score: float
    confidence: float
    freshness: float = 0.0
    urgency: float = 0.0
    is_reply: bool = False


class DistributionService:
    """Coordinates natural decisioning, policy, permission, rate limiting and routing."""

    def __init__(self, router: DistributionRouter, *, permissions: PermissionPolicy | None = None,
                 policy: DistributionPolicyEngine | None = None, natural: NaturalPublishingEngine | None = None,
                 limiter: RateLimiter | None = None, events: EventBus | None = None,
                 audit: AuditLog | None = None) -> None:
        self.router = router
        self.permissions = permissions or PermissionPolicy()
        self.policy = policy or DistributionPolicyEngine()
        self.natural = natural or NaturalPublishingEngine()
        self.limiter = limiter or RateLimiter()
        self.events = events or EventBus()
        self.audit = audit or AuditLog()

    def publish(self, request: PublishRequest, *, owner_approved: bool = False) -> DistributionResult:
        destination = request.destination
        candidate = PublishingCandidate(request.value_score, request.confidence, request.freshness, request.urgency)
        natural = self.natural.decide(candidate)
        self.audit.record(AuditRecord("distribution.decided", details={"destination": destination.destination_id, "decision": natural.decision.value, "score": natural.score}))
        self.events.publish(RuntimeEvent("distribution.decided", {"destination": destination.destination_id, "decision": natural.decision.value}))
        if natural.decision != PublicationDecision.SPEAK:
            return DistributionResult(False, destination.destination_id, reason=natural.reason)
        policy = self.policy.evaluate(destination, value_score=request.value_score, confidence=request.confidence, is_reply=request.is_reply)
        if policy.decision != PublicationDecision.SPEAK:
            return DistributionResult(False, destination.destination_id, reason=policy.reason)
        if not self.limiter.allow(destination.destination_id):
            return DistributionResult(False, destination.destination_id, reason="destination rate limit reached")
        action = ActionRequest("distribution.publish", ActionRisk.LOW, reason="approved distribution candidate")
        try:
            self.permissions.check(action, owner_approved=owner_approved)
        except PermissionDenied as exc:
            self.audit.record(AuditRecord("distribution.denied", action=action.action, success=False, details={"reason": str(exc)}))
            return DistributionResult(False, destination.destination_id, reason=str(exc))
        self.events.publish(RuntimeEvent("distribution.publish_requested", {"destination": destination.destination_id}))
        result = self.router.route(request.message)
        self.audit.record(AuditRecord("distribution.completed", action=action.action, success=result.accepted, details={"destination": destination.destination_id, "reason": result.reason, "message_id": result.message_id}))
        self.events.publish(RuntimeEvent("distribution.completed", {"destination": destination.destination_id, "accepted": result.accepted}))
        return result
