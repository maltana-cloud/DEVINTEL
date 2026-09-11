"""Provider contracts. External credentials and side effects stay outside core."""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Mapping


class ProviderCapability(str, Enum):
    RESEARCH = "research"
    PUBLISH = "publish"
    PAYMENT = "payment"
    DEPLOY = "deploy"
    GENERATION = "generation"


@dataclass(frozen=True)
class ProviderHealth:
    """Observable provider health; health does not grant provider authority."""

    provider_id: str
    healthy: bool
    message: str = ""
    metadata: Mapping[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.provider_id, str) or not self.provider_id.strip():
            raise ValueError("provider_id is required")
        if not isinstance(self.healthy, bool):
            raise ValueError("healthy must be a bool")
        if not isinstance(self.message, str):
            raise ValueError("message must be a string")
        if self.metadata is None:
            raise ValueError("metadata must not be None")


@dataclass(frozen=True)
class ProviderResult:
    """Provider output envelope; callers still enforce permission and verification."""

    provider_id: str
    success: bool
    output: object = None
    error: str = ""

    def __post_init__(self) -> None:
        if not isinstance(self.provider_id, str) or not self.provider_id.strip():
            raise ValueError("provider_id is required")
        if not isinstance(self.success, bool):
            raise ValueError("success must be a bool")
        if not isinstance(self.error, str):
            raise ValueError("error must be a string")
        if self.success and self.error:
            raise ValueError("successful result cannot contain an error")
