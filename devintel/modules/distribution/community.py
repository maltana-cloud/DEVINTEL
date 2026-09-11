"""Explicit, fail-closed community discovery/join participation boundary."""

from dataclasses import dataclass
from typing import Callable

from .contracts import DestinationKind, DistributionDestination, DistributionResult


@dataclass(frozen=True)
class ParticipationRequest:
    destination: DistributionDestination
    reason: str
    owner_approved: bool = False


@dataclass(frozen=True)
class ParticipationResult:
    accepted: bool
    reason: str


JoinTransport = Callable[[str], bool]


class CommunityParticipation:
    """Joining is opt-in and transport-authorized; discovery never implies joining."""

    def __init__(self, join_transport: JoinTransport | None = None) -> None:
        self._join_transport = join_transport

    def request(self, request: ParticipationRequest) -> ParticipationResult:
        if request.destination.kind not in {DestinationKind.COMMUNITY, DestinationKind.GROUP, DestinationKind.DISCUSSION}:
            return ParticipationResult(False, "destination is not a community participation target")
        if not request.reason.strip():
            return ParticipationResult(False, "participation reason is required")
        if not request.owner_approved:
            return ParticipationResult(False, "owner approval is required to join or participate")
        if self._join_transport is None:
            return ParticipationResult(False, "community transport is not configured")
        try:
            if self._join_transport(request.destination.destination_id):
                return ParticipationResult(True, "participation transport accepted request")
            return ParticipationResult(False, "platform declined participation request")
        except Exception as exc:
            return ParticipationResult(False, f"participation transport failure: {type(exc).__name__}")
