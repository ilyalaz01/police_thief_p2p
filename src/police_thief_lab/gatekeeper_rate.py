"""Thread-safe sliding-window rate admission for the API gatekeeper."""

from __future__ import annotations

import threading
from collections import deque
from collections.abc import Callable

from .gatekeeper_models import RateLimitConfig


class RateWindow:
    """Enforce minute/hour limits before every external call attempt."""

    def __init__(
        self,
        config: RateLimitConfig,
        clock: Callable[[], float],
        sleep: Callable[[float], None],
    ) -> None:
        """Initialize RateWindow with its validated setup values and private state."""
        self._config = config
        self._clock = clock
        self._sleep = sleep
        self._lock = threading.Lock()
        self._minute: deque[float] = deque()
        self._hour: deque[float] = deque()

    def wait(self) -> bool:
        """Block until admitted and return whether a rate wait occurred."""
        waited = False
        while True:
            with self._lock:
                now = self._clock()
                while self._minute and self._minute[0] <= now - 60.0:
                    self._minute.popleft()
                while self._hour and self._hour[0] <= now - 3600.0:
                    self._hour.popleft()
                minute_wait = (
                    self._minute[0] + 60.0 - now
                    if len(self._minute) >= self._config.requests_per_minute
                    else 0.0
                )
                hour_wait = (
                    self._hour[0] + 3600.0 - now
                    if len(self._hour) >= self._config.requests_per_hour
                    else 0.0
                )
                delay = max(minute_wait, hour_wait)
                if delay <= 0.0:
                    self._minute.append(now)
                    self._hour.append(now)
                    return waited
            waited = True
            self._sleep(delay)
