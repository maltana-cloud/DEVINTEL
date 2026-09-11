"""Explicit, read-only adapters from adjacent DEVINTEL systems into Education.

These adapters share signals, not authority. Providers are host-controlled and
replaceable; a failing provider is isolated from the education plan.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Mapping, Protocol, Sequence


@dataclass(frozen=True)
class EducationIntegrationSignal:
    source: str
    scope_id: str
    domain: str
    kind: str
    value: Any = None
    metadata: Mapping[str, Any] = ()

    def __post_init__(self) -> None:
        if not self.source.strip() or not self.scope_id.strip() or not self.domain.strip() or not self.kind.strip():
            raise ValueError("source, scope_id, domain, and kind are required")


@dataclass(frozen=True)
class EducationIntegrationResult:
    scope_id: str
    domain: str
    signals: tuple[EducationIntegrationSignal, ...]
    failed_sources: tuple[str, ...] = ()


class ConversationMemoryAdapter(Protocol):
    def learning_context(self, scope_id: str, learner_id: str, domain: str) -> Sequence[str]: ...


class OpportunityAdapter(Protocol):
    def learning_needs(self, scope_id: str, domain: str) -> Sequence[str]: ...


class ToolBuilderAdapter(Protocol):
    def apprenticeship_needs(self, scope_id: str, domain: str) -> Sequence[str]: ...


class GrowthAdapter(Protocol):
    def learning_signals(self, scope_id: str, domain: str) -> Sequence[str]: ...


class BusinessAdapter(Protocol):
    def education_needs(self, scope_id: str, domain: str) -> Sequence[str]: ...


class StrategyAdapter(Protocol):
    def domain_priorities(self, scope_id: str, domain: str) -> Sequence[str]: ...


class DistributionAdapter(Protocol):
    def channel_context(self, scope_id: str, domain: str) -> Sequence[str]: ...


class MonitoringAdapter(Protocol):
    def education_health(self, scope_id: str, domain: str) -> str: ...


@dataclass(frozen=True)
class _AdapterSpec:
    source: str
    method: str
    build_kind: str


class EducationSubsystemIntegration:
    """Collects bounded signals from other systems without granting authority."""

    _SPECS = (
        _AdapterSpec("conversation", "learning_context", "learner_context"),
        _AdapterSpec("opportunity", "learning_needs", "learning_need"),
        _AdapterSpec("tool_builder", "apprenticeship_needs", "apprenticeship_need"),
        _AdapterSpec("growth", "learning_signals", "growth_signal"),
        _AdapterSpec("business", "education_needs", "commercial_need"),
        _AdapterSpec("strategy", "domain_priorities", "strategic_priority"),
        _AdapterSpec("distribution", "channel_context", "channel_context"),
        _AdapterSpec("monitoring", "education_health", "health"),
    )

    def __init__(self, **adapters: object) -> None:
        unknown = set(adapters) - {spec.source for spec in self._SPECS}
        if unknown:
            raise ValueError(f"unknown education adapters: {sorted(unknown)}")
        self._adapters = dict(adapters)

    def collect(self, scope_id: str, domain: str, *, learner_id: str = "") -> EducationIntegrationResult:
        scope = scope_id.strip() if isinstance(scope_id, str) else ""
        subject = domain.strip() if isinstance(domain, str) else ""
        learner = learner_id.strip() if isinstance(learner_id, str) else ""
        if not scope or not subject:
            raise ValueError("scope_id and domain are required")
        signals: list[EducationIntegrationSignal] = []
        failures: list[str] = []
        for spec in self._SPECS:
            adapter = self._adapters.get(spec.source)
            if adapter is None:
                continue
            method = getattr(adapter, spec.method, None)
            if not callable(method):
                failures.append(spec.source)
                continue
            try:
                if spec.source == "conversation":
                    raw = method(scope, learner, subject)
                elif spec.source == "monitoring":
                    raw = (method(scope, subject),)
                else:
                    raw = method(scope, subject)
                if isinstance(raw, str):
                    raw = (raw,)
                for item in raw:
                    if isinstance(item, str) and item.strip():
                        signals.append(EducationIntegrationSignal(spec.source, scope, subject, spec.build_kind, item.strip()))
                    elif isinstance(item, Mapping):
                        signals.append(EducationIntegrationSignal(spec.source, scope, subject, spec.build_kind, dict(item)))
            except Exception:
                failures.append(spec.source)
        return EducationIntegrationResult(scope, subject, tuple(signals), tuple(dict.fromkeys(failures)))
