"""Deterministic contract for centralized external-call admission and monitoring."""

from __future__ import annotations

import threading
import time
from pathlib import Path

import pytest

from police_thief_lab.gatekeeper import (
    ApiGatekeeper,
    GatekeeperBackpressure,
    RateLimitConfig,
    load_rate_limit_config,
)
from police_thief_lab.interop.transport import McpPeerClient

ROOT = Path(__file__).parents[1]


def _config(**overrides: int) -> RateLimitConfig:
    values = {
        "requests_per_minute": 1000,
        "requests_per_hour": 10000,
        "concurrent_max": 1,
        "queue_max": 2,
        "monitoring_max": 16,
    }
    values.update(overrides)
    return RateLimitConfig("1.0", "fastmcp", **values)


def _wait_for(predicate, timeout: float = 1.0) -> None:
    deadline = time.monotonic() + timeout
    while not predicate():
        if time.monotonic() >= deadline:
            raise AssertionError("condition did not become true")
        time.sleep(0.001)


def test_tracked_rate_limit_config_is_strict_and_versioned() -> None:
    path = ROOT / "config/rate_limits.v1.json"
    config = load_rate_limit_config(path, "fastmcp")
    assert config.schema_version == "1.0"
    assert config.service == "fastmcp"
    assert config.concurrent_max == 1
    assert config.queue_max > 0


def test_gatekeeper_queues_fifo_and_signals_only_when_bounded_queue_is_full() -> None:
    gate = ApiGatekeeper(_config())
    first_started = threading.Event()
    release = threading.Event()
    order: list[str] = []
    results: list[str] = []

    def call(name: str) -> str:
        order.append(name)
        if name == "first":
            first_started.set()
            release.wait(1.0)
        return name

    threads = []
    for name, queued in (("first", 0), ("second", 1), ("third", 2)):
        thread = threading.Thread(
            target=lambda value=name: results.append(
                gate.execute(call, value, operation="fastmcp.test")
            )
        )
        thread.start()
        threads.append(thread)
        if name == "first":
            assert first_started.wait(1.0)
        else:
            _wait_for(lambda expected=queued: gate.get_queue_status().queued == expected)
    with pytest.raises(GatekeeperBackpressure, match="queue is full"):
        gate.execute(lambda: None, operation="fastmcp.overflow")
    release.set()
    for thread in threads:
        thread.join(1.0)
    assert order == ["first", "second", "third"]
    assert sorted(results) == ["first", "second", "third"]
    assert gate.drain(1.0)
    gate.close()


def test_rate_limit_waits_before_the_next_call_using_injected_time() -> None:
    now = [0.0]
    sleeps: list[float] = []

    def sleep(seconds: float) -> None:
        sleeps.append(seconds)
        now[0] += seconds

    gate = ApiGatekeeper(
        _config(requests_per_minute=1),
        clock=lambda: now[0],
        sleep=sleep,
    )
    assert gate.execute(lambda: "a", operation="fastmcp.a") == "a"
    assert gate.execute(lambda: "b", operation="fastmcp.b") == "b"
    assert sleeps == [60.0]
    assert gate.get_queue_status().rate_waits == 1
    gate.close()


def test_monitoring_is_bounded_and_never_retains_arguments_or_values() -> None:
    gate = ApiGatekeeper(_config(monitoring_max=2))
    secret = "synthetic-secret-value"
    assert gate.execute(lambda value: len(value), secret, operation="fastmcp.safe") == len(secret)
    with pytest.raises(ValueError, match="synthetic failure"):
        gate.execute(
            lambda: (_ for _ in ()).throw(ValueError("synthetic failure")),
            operation="fastmcp.failure",
        )
    gate.execute(lambda: None, operation="fastmcp.last")
    metrics = gate.get_metrics()
    assert len(metrics) == 2
    assert {metric.outcome for metric in metrics} == {"success", "failure"}
    assert secret not in repr(metrics)
    gate.close()


def test_mcp_client_routes_every_transport_attempt_through_injected_gatekeeper(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    operations = []
    gate = ApiGatekeeper(_config())
    original = gate.execute

    def observed(api_call, *args, **kwargs):
        operations.append(kwargs["operation"])
        return original(api_call, *args, **kwargs)

    monkeypatch.setattr(gate, "execute", observed)
    client = McpPeerClient("http://127.0.0.1:1/mcp", 1.0, 0.0, gatekeeper=gate)
    monkeypatch.setattr(client, "_invoke", lambda *_args: None)
    client.call("receive_turn", {"step": 1})
    assert operations == ["fastmcp.receive_turn"]
    gate.close()
