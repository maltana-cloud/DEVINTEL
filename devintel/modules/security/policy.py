"""Fail-closed security policy and untrusted-input boundary."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable

from .contracts import SecurityState, ThreatLevel


class InputTrust(str, Enum):
    UNTRUSTED = "UNTRUSTED"
    INTERNAL = "INTERNAL"
    OWNER = "OWNER"


@dataclass(frozen=True)
class SecurityPolicy:
    state: SecurityState = SecurityState.NORMAL
    emergency_stop: bool = False
    allowed_scopes: frozenset[str] = frozenset()

    def authorize(self, scope: str, risk: ThreatLevel) -> bool:
        if not scope or self.emergency_stop:
            return False
        if self.state in {SecurityState.CONTAINMENT, SecurityState.RECOVERY, SecurityState.SAFE_DEGRADED}:
            return False
        if self.allowed_scopes and scope not in self.allowed_scopes:
            return False
        if risk in {ThreatLevel.HIGH, ThreatLevel.CRITICAL}:
            return False
        return True

    @staticmethod
    def classify_external(value: object) -> InputTrust:
        # External text/data can never become authority merely by containing
        # commands, role markers, or prompt-injection language.
        return InputTrust.UNTRUSTED

    def with_state(self, state: SecurityState) -> "SecurityPolicy":
        return SecurityPolicy(state, self.emergency_stop, self.allowed_scopes)

    def restrict_to(self, scopes: Iterable[str]) -> "SecurityPolicy":
        return SecurityPolicy(self.state, self.emergency_stop, frozenset(s for s in scopes if s))
