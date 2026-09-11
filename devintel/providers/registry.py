"""Thread-safe provider registry with isolated capabilities."""
from __future__ import annotations
from threading import RLock
from typing import Any

class ProviderRegistry:
    def __init__(self, max_providers: int = 256) -> None:
        if max_providers <= 0: raise ValueError("max_providers must be positive")
        self._max = max_providers
        self._providers: dict[str, Any] = {}
        self._lock = RLock()

    def register(self, provider_id: str, provider: Any) -> None:
        if not isinstance(provider_id, str) or not provider_id.strip():
            raise ValueError("provider_id is required")
        if provider is None: raise ValueError("provider is required")
        with self._lock:
            if provider_id not in self._providers and len(self._providers) >= self._max:
                raise RuntimeError("provider registry capacity reached")
            self._providers[provider_id] = provider

    def get(self, provider_id: str) -> Any | None:
        with self._lock: return self._providers.get(provider_id)

    def remove(self, provider_id: str) -> bool:
        with self._lock: return self._providers.pop(provider_id, None) is not None

    def ids(self) -> tuple[str, ...]:
        with self._lock: return tuple(sorted(self._providers))
