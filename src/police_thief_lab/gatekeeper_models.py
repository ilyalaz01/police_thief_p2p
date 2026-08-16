"""Typed, versioned API-gatekeeper configuration and sanitized status models."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

RATE_LIMIT_SCHEMA_VERSION = "1.0"
_ROOT_FIELDS = frozenset({"schema_version", "services"})
_SERVICE_FIELDS = frozenset(
    {
        "requests_per_minute",
        "requests_per_hour",
        "concurrent_max",
        "queue_max",
        "monitoring_max",
    }
)


class GatekeeperBackpressure(RuntimeError):  # noqa: N818 - required domain signal name
    """Signal that the configured bounded waiting queue has reached capacity."""


@dataclass(frozen=True, slots=True)
class RateLimitConfig:
    """Validated limits for one named external service."""

    schema_version: str
    service: str
    requests_per_minute: int
    requests_per_hour: int
    concurrent_max: int
    queue_max: int
    monitoring_max: int


@dataclass(frozen=True, slots=True)
class QueueStatus:
    """Sanitized aggregate state with no URL, argument, payload, or credential."""

    queued: int
    in_flight: int
    completed: int
    failed: int
    rate_waits: int
    high_watermark: int


@dataclass(frozen=True, slots=True)
class CallMetric:
    """Bounded per-call metadata that never retains request or response bodies."""

    operation: str
    outcome: str
    duration_ms: float
    error_type: str | None


def _positive_integer(value: Any, field: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value < 1:
        raise ValueError(f"rate-limit {field} must be a positive integer")
    return value


def load_rate_limit_config(path: Path, service: str) -> RateLimitConfig:
    """Load one strict service policy from the versioned JSON document."""
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ValueError("invalid rate-limit config JSON") from exc
    if not isinstance(raw, dict) or frozenset(raw) != _ROOT_FIELDS:
        raise ValueError("rate-limit root fields mismatch")
    if raw["schema_version"] != RATE_LIMIT_SCHEMA_VERSION:
        raise ValueError(f"unsupported rate-limit schema: {raw['schema_version']}")
    services = raw["services"]
    if not isinstance(services, dict) or service not in services:
        raise ValueError(f"rate-limit service is missing: {service}")
    values = services[service]
    if not isinstance(values, dict) or frozenset(values) != _SERVICE_FIELDS:
        raise ValueError(f"rate-limit fields mismatch for service: {service}")
    return RateLimitConfig(
        RATE_LIMIT_SCHEMA_VERSION,
        service,
        _positive_integer(values["requests_per_minute"], "requests_per_minute"),
        _positive_integer(values["requests_per_hour"], "requests_per_hour"),
        _positive_integer(values["concurrent_max"], "concurrent_max"),
        _positive_integer(values["queue_max"], "queue_max"),
        _positive_integer(values["monitoring_max"], "monitoring_max"),
    )


def default_rate_limit_path() -> Path:
    """Resolve an operator override or the tracked repository policy."""
    override = os.environ.get("POLICE_THIEF_RATE_LIMITS_PATH")
    if override:
        return Path(override)
    return Path(__file__).resolve().parents[2] / "config/rate_limits.v1.json"
