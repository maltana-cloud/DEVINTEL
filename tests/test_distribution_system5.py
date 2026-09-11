from devintel.modules.distribution import (
    CommunityParticipation, DestinationKind, DistributionDestination, DistributionMessage,
    DistributionResult, DistributionRouter, DistributionService, NaturalPublishingEngine,
    ParticipationRequest, PublishingCandidate, RateLimiter, TelegramAdapter, PublicationDecision,
    PublishRequest,
)


def dest(kind=DestinationKind.CHANNEL, ident="channel:a"):
    return DistributionDestination(ident, kind, "telegram")


def test_natural_engine_prefers_silence_and_defers():
    engine = NaturalPublishingEngine()
    assert engine.decide(PublishingCandidate(.2, .9)).decision == PublicationDecision.STAY_QUIET
    assert engine.decide(PublishingCandidate(.7, .7, .2)).decision in {PublicationDecision.DEFER, PublicationDecision.SPEAK}
    assert engine.decide(PublishingCandidate(.9, .9, .9, .9)).decision == PublicationDecision.SPEAK


def test_rate_limit_isolated_per_destination():
    limiter = RateLimiter(max_actions=1, window_seconds=60)
    assert limiter.allow("a")
    assert not limiter.allow("a")
    assert limiter.allow("b")


def test_service_publishes_only_after_all_gates():
    router = DistributionRouter()
    router.register("channel:a", lambda m: DistributionResult(True, m.destination_id, "42"))
    service = DistributionService(router)
    result = service.publish(PublishRequest(dest(), DistributionMessage("channel:a", "useful update"), .95, .95, .9, .8))
    assert result.accepted and result.message_id == "42"
    assert any(r.event == "distribution.completed" and r.success for r in service.audit.history())


def test_service_never_sends_low_value_content():
    called = []
    router = DistributionRouter()
    router.register("channel:a", lambda m: called.append(m) or DistributionResult(True, m.destination_id, "1"))
    service = DistributionService(router)
    result = service.publish(PublishRequest(dest(), DistributionMessage("channel:a", "noise"), .1, .9))
    assert not result.accepted
    assert called == []


def test_community_join_requires_owner_approval_and_transport():
    calls = []
    participation = CommunityParticipation(lambda ident: calls.append(ident) or True)
    request = ParticipationRequest(dest(DestinationKind.GROUP, "group:x"), "relevant developer discussion")
    assert not participation.request(request).accepted
    approved = participation.request(ParticipationRequest(request.destination, request.reason, True))
    assert approved.accepted and calls == ["group:x"]


def test_telegram_adapter_is_provider_boundary():
    adapter = TelegramAdapter(lambda ident, text: "telegram-7")
    result = adapter.send(dest(), DistributionMessage("channel:a", "hello"))
    assert result.accepted and result.message_id == "telegram-7"
    assert not TelegramAdapter().send(dest(), DistributionMessage("channel:a", "hello")).accepted
