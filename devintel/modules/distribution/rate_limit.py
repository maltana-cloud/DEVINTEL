"""Provider-independent rate limiting for distribution actions."""

from collections import deque
from threading import RLock
from time import monotonic


class RateLimiter:
    """Sliding-window limiter isolated per destination."""

    def __init__(self, max_actions: int = 5, window_seconds: float = 3600.0) -> None:
        if max_actions < 0 or window_seconds <= 0:
            raise ValueError("invalid rate limit")
        self.max_actions = max_actions
        self.window_seconds = window_seconds
        self._events: dict[str, deque[float]] = {}
        self._lock = RLock()

    def allow(self, scope_id: str) -> bool:
        if not scope_id.strip():
            return False
        now = monotonic()
        with self._lock:
            q = self._events.setdefault(scope_id, deque())
            cutoff = now - self.window_seconds
            while q and q[0] <= cutoff:
                q.popleft()
            if len(q) >= self.max_actions:
                return False
            q.append(now)
            return True

    def remaining(self, scope_id: str) -> int:
        now = monotonic()
        with self._lock:
            q = self._events.get(scope_id, deque())
            cutoff = now - self.window_seconds
            while q and q[0] <= cutoff:
                q.popleft()
            return max(0, self.max_actions - len(q))
