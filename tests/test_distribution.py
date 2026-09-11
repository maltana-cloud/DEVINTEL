from devintel.modules.distribution import (
    DestinationKind,
    DistributionDestination,
    DistributionMessage,
    DistributionPolicyEngine,
    DistributionResult,
    DistributionRouter,
    PublicationDecision,
    PublicationPolicy,
)


def destination(kind=DestinationKind.CHANNEL, destination_id="channel:a"):
    return DistributionDestination(destination_id, kind, "test")


def test_policy_stays_quiet_for_low_value_or_confidence():
    engine = DistributionPolicyEngine()
    assert engine.evaluate(destination(), value_score=0.4, confidence=0.9).decision == PublicationDecision.STAY_QUIET
    assert engine.evaluate(destination(), value_score=0.9, confidence=0.4).decision == PublicationDecision.STAY_QUIET


def test_community_participation_is_fail_closed_by_default():
    engine = DistributionPolicyEngine()
    result = engine.evaluate(
        destination(DestinationKind.GROUP),
        value_score=0.9,
        confidence=0.9,
        requested_community_participation=True,
    )
    assert result.decision == PublicationDecision.REJECT


def test_community_participation_can_be_explicitly_enabled():
    engine = DistributionPolicyEngine(PublicationPolicy(allow_community_participation=True))
    result = engine.evaluate(
        destination(DestinationKind.GROUP),
        value_score=0.9,
        confidence=0.9,
        requested_community_participation=True,
    )
    assert result.decision == PublicationDecision.SPEAK


def test_router_isolates_adapter_failure():
    router = DistributionRouter()

    def broken(_):
        raise RuntimeError("boom")

    router.register("channel:a", broken)
    router.register("channel:b", lambda m: DistributionResult(True, m.destination_id, "msg-1"))

    failed = router.route(DistributionMessage("channel:a", "hello"))
    succeeded = router.route(DistributionMessage("channel:b", "hello"))

    assert not failed.accepted
    assert succeeded.accepted


def test_router_fails_closed_when_destination_is_unregistered():
    result = DistributionRouter().route(DistributionMessage("missing", "hello"))
    assert not result.accepted
    assert "no registered" in result.reason


def test_router_rejects_adapter_destination_mismatch():
    router = DistributionRouter()
    router.register("channel:a", lambda m: DistributionResult(True, "channel:b", "msg-1"))
    result = router.route(DistributionMessage("channel:a", "hello"))
    assert not result.accepted
