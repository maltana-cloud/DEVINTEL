"""Provider contracts. External credentials and side effects stay outside core."""
from __future__ import annotations
from dataclasses import dataclass
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
    provider_id: str
    healthy: bool
    message: str = ""
    metadata: Mapping[str, str] = None

@dataclass(frozen=True)
class ProviderResult:
    provider_id: str
    success: bool
    output: object = None
    error: str = ""
