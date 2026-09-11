"""Provider-independent contracts for distribution and community actions."""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Mapping


class DestinationKind(str, Enum):
    CHANNEL = "channel"
    GROUP = "group"
    COMMUNITY = "community"
    DISCUSSION = "discussion"
    PRIVATE = "private"


class PublicationDecision(str, Enum):
    SPEAK = "speak"
    STAY_QUIET = "stay_quiet"
    DEFER = "defer"
    REJECT = "reject"


@dataclass(frozen=True)
class DistributionDestination:
    destination_id: str
    kind: DestinationKind
    platform: str
    audience: str = ""
    metadata: Mapping[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.destination_id.strip():
            raise ValueError("destination_id must not be empty")
        if not self.platform.strip():
            raise ValueError("platform must not be empty")


@dataclass(frozen=True)
class DistributionMessage:
    destination_id: str
    text: str
    source_event_id: str = ""
    reply_to_id: str = ""
    metadata: Mapping[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.destination_id.strip():
            raise ValueError("destination_id must not be empty")
        if not self.text.strip():
            raise ValueError("text must not be empty")


@dataclass(frozen=True)
class DistributionResult:
    accepted: bool
    destination_id: str
    message_id: str = ""
    reason: str = ""
    observed_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self) -> None:
        if self.observed_at.tzinfo is None:
            raise ValueError("observed_at must be timezone-aware")


@dataclass(frozen=True)
class PublicationPolicy:
    """Bounded policy inputs; platform permissions remain authoritative elsewhere."""

    min_value_score: float = 0.65
    min_confidence: float = 0.60
    allow_replies: bool = True
    allow_proactive_posts: bool = True
    allow_community_participation: bool = False
    max_posts_per_window: int = 5
    window_seconds: int = 3600

    def __post_init__(self) -> None:
        if not 0 <= self.min_value_score <= 1:
            raise ValueError("min_value_score must be between 0 and 1")
        if not 0 <= self.min_confidence <= 1:
            raise ValueError("min_confidence must be between 0 and 1")
        if self.max_posts_per_window < 0 or self.window_seconds <= 0:
            raise ValueError("publication limits must be non-negative and bounded")


@dataclass(frozen=True)
class PublicationPolicyResult:
    decision: PublicationDecision
    reason: str

