"""Central FIFO admission, rate limiting, backpressure, drain, and safe monitoring."""

from __future__ import annotations

import queue
import threading
import time
from collections import deque
from collections.abc import Callable
from functools import lru_cache
from typing import Any

from .gatekeeper_models import (
    CallMetric,
    GatekeeperBackpressure,
    QueueStatus,
    RateLimitConfig,
    default_rate_limit_path,
    load_rate_limit_config,
)
from .gatekeeper_rate import RateWindow
from .gatekeeper_work import WorkItem


class ApiGatekeeper:
    """Execute external calls through a bounded FIFO and versioned rate policy."""

    def __init__(
        self,
        config: RateLimitConfig,
        *,
        clock: Callable[[], float] = time.monotonic,
        sleep: Callable[[float], None] = time.sleep,
    ) -> None:
        """Initialize ApiGatekeeper with its validated setup values and private state."""
        self.config = config
        self._clock, self._sleep = clock, sleep
        self._queue: queue.Queue[WorkItem] = queue.Queue(config.queue_max)
        self._lock = threading.Lock()
        self._metrics: deque[CallMetric] = deque(maxlen=config.monitoring_max)
        self._rate = RateWindow(config, clock, sleep)
        self._in_flight = self._completed = self._failed = self._rate_waits = 0
        self._pending = 0
        self._high_watermark = 0
        self._closed = False
        self._workers = tuple(
            threading.Thread(target=self._worker, daemon=True, name=f"api-gatekeeper-{index}")
            for index in range(config.concurrent_max)
        )
        for worker in self._workers:
            worker.start()

    def execute(
        self,
        api_call: Callable[..., Any],
        *args: Any,
        operation: str = "external.call",
        **kwargs: Any,
    ) -> Any:
        """Queue one call or emit explicit backpressure when the bounded queue is full."""
        item = WorkItem(api_call, args, kwargs, operation)
        with self._lock:
            if self._closed:
                raise RuntimeError("gatekeeper is closed")
            try:
                self._queue.put_nowait(item)
            except queue.Full as exc:
                raise GatekeeperBackpressure("gatekeeper queue is full") from exc
            self._pending += 1
            self._high_watermark = max(self._high_watermark, self._queue.qsize())
        item.done.wait()
        result, error = item.result, item.error
        item.args = ()
        item.kwargs.clear()
        item.result = item.error = None
        if error is not None:
            raise error
        return result

    def _worker(self) -> None:
        """Compute the internal worker step used by ApiGatekeeper."""
        while True:
            try:
                item = self._queue.get(timeout=0.01)
            except queue.Empty:
                with self._lock:
                    if self._closed and self._pending == 0:
                        return
                continue
            if self._rate.wait():
                with self._lock:
                    self._rate_waits += 1
            started = self._clock()
            with self._lock:
                self._in_flight += 1
            try:
                item.result = item.api_call(*item.args, **item.kwargs)
                outcome, error_type = "success", None
            except BaseException as exc:  # preserve the established transport exception exactly
                item.error = exc
                outcome, error_type = "failure", type(exc).__name__
            with self._lock:
                self._in_flight -= 1
                self._completed += outcome == "success"
                self._failed += outcome == "failure"
                self._pending -= 1
                self._metrics.append(
                    CallMetric(
                        item.operation,
                        outcome,
                        (self._clock() - started) * 1000,
                        error_type,
                    )
                )
            item.done.set()
            self._queue.task_done()

    def get_queue_status(self) -> QueueStatus:
        """Return sanitized bounded-queue counters."""
        with self._lock:
            return QueueStatus(
                self._queue.qsize(), self._in_flight, self._completed, self._failed,
                self._rate_waits, self._high_watermark,
            )

    def get_metrics(self) -> tuple[CallMetric, ...]:
        """Return a snapshot containing no request or response values."""
        with self._lock:
            return tuple(self._metrics)

    def drain(self, timeout: float) -> bool:
        """Wait until queued and active calls complete, bounded by a caller timeout."""
        deadline = self._clock() + timeout
        while self._clock() < deadline:
            with self._lock:
                if self._pending == 0:
                    return True
            self._sleep(0.001)
        return False

    def close(self) -> None:
        """Drain completed work and stop daemon workers without discarding queued calls."""
        with self._lock:
            self._closed = True
        if not self.drain(1.0):
            raise TimeoutError("gatekeeper drain deadline")
        for worker in self._workers:
            worker.join(1.0)
        if any(worker.is_alive() for worker in self._workers):
            raise TimeoutError("gatekeeper worker shutdown deadline")


@lru_cache(maxsize=1)
def default_gatekeeper() -> ApiGatekeeper:
    """Return the process-wide FastMCP gatekeeper loaded from versioned configuration."""
    return ApiGatekeeper(load_rate_limit_config(default_rate_limit_path(), "fastmcp"))


__all__ = [
    "ApiGatekeeper", "CallMetric", "GatekeeperBackpressure", "QueueStatus", "RateLimitConfig",
    "default_gatekeeper", "load_rate_limit_config",
]
