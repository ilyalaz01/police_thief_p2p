"""RED contracts for Gatekeeper lifecycle races, cleanup, and capacity."""

from __future__ import annotations

import threading
import time
from collections.abc import Callable

import pytest

from police_thief_lab.gatekeeper import ApiGatekeeper, GatekeeperBackpressure, RateLimitConfig


def _config(*, workers: int = 1, queued: int = 2) -> RateLimitConfig:
    return RateLimitConfig("1.0", "fastmcp", 1000, 10000, workers, queued, 16)


def _wait_for(predicate: Callable[[], bool], timeout: float = 1.0) -> bool:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if predicate():
            return True
        time.sleep(0.001)
    return predicate()


def test_execute_admission_and_close_cannot_strand_work(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    gate = ApiGatekeeper(_config())
    entered_put = threading.Event()
    release_put = threading.Event()
    original_put = gate._queue.put_nowait
    results: list[str] = []
    errors: list[BaseException] = []

    def blocked_put(item: object) -> None:
        entered_put.set()
        assert release_put.wait(1.0)
        original_put(item)

    def execute() -> None:
        try:
            results.append(gate.execute(lambda: "done"))
        except BaseException as exc:
            errors.append(exc)

    def close() -> None:
        try:
            gate.close()
        except BaseException as exc:
            errors.append(exc)

    monkeypatch.setattr(gate._queue, "put_nowait", blocked_put)
    caller = threading.Thread(target=execute, daemon=True)
    closer = threading.Thread(target=close, daemon=True)
    caller.start()
    assert entered_put.wait(1.0)
    closer.start()
    release_put.set()
    caller.join(1.0)
    closer.join(1.0)
    assert not caller.is_alive() and not closer.is_alive()
    assert errors == []
    assert results == ["done"]


def test_close_timeout_eventually_reaps_workers_after_call_finishes() -> None:
    gate = ApiGatekeeper(_config())
    started = threading.Event()
    release = threading.Event()

    def blocking_call() -> None:
        started.set()
        assert release.wait(2.0)

    caller = threading.Thread(target=lambda: gate.execute(blocking_call), daemon=True)
    caller.start()
    assert started.wait(1.0)
    with pytest.raises(TimeoutError, match="gatekeeper drain deadline"):
        gate.close()
    release.set()
    caller.join(1.0)
    assert not caller.is_alive()
    assert _wait_for(lambda: not any(worker.is_alive() for worker in gate._workers))
    gate.close()


def test_configured_workers_and_queue_define_exact_bounded_capacity() -> None:
    gate = ApiGatekeeper(_config(workers=2, queued=3))
    release = threading.Event()
    results: list[int] = []

    def call(value: int) -> int:
        assert release.wait(1.0)
        return value

    callers = [
        threading.Thread(target=lambda value=value: results.append(gate.execute(call, value)))
        for value in range(5)
    ]
    for caller in callers[:2]:
        caller.start()
    assert _wait_for(lambda: gate.get_queue_status().in_flight == 2)
    for caller in callers[2:]:
        caller.start()
    assert _wait_for(lambda: gate.get_queue_status().queued == 3)
    with pytest.raises(GatekeeperBackpressure, match="queue is full"):
        gate.execute(lambda: None)
    release.set()
    for caller in callers:
        caller.join(1.0)
    assert not any(caller.is_alive() for caller in callers)
    assert sorted(results) == list(range(5))
    status = gate.get_queue_status()
    assert (status.queued, status.in_flight, status.completed, status.failed) == (0, 0, 5, 0)
    assert status.high_watermark == 3
    gate.close()
