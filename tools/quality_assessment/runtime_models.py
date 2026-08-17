"""Pure records and arithmetic for local simulator performance evidence."""

from __future__ import annotations

import math
from dataclasses import dataclass
from statistics import fmean


@dataclass(frozen=True, slots=True)
class TimingSample:
    """One instrumented local game timing and serialized-result observation."""

    seed: int
    wall_ns: int
    cpu_ns: int
    result_bytes: int
    result_sha256: str
    illegal_actions: int


@dataclass(frozen=True, slots=True)
class MemorySample:
    """One tracemalloc peak for Python allocations during a local game."""

    seed: int
    peak_python_bytes: int


def _require(values: tuple[float, ...]) -> tuple[float, ...]:
    """Reject an evidence summary without retained observations."""
    if not values:
        raise ValueError("measurement samples must not be empty")
    return tuple(sorted(values))


def _nearest_rank(values: tuple[float, ...], percentile: float) -> float:
    """Return the declared nearest-rank percentile from sorted values."""
    ordered = _require(values)
    return ordered[max(0, math.ceil(percentile * len(ordered)) - 1)]


def _distribution(values: tuple[float, ...], divisor: float) -> dict[str, float]:
    """Summarize raw values after converting them with divisor."""
    ordered = _require(values)
    return {
        "mean": fmean(ordered) / divisor,
        "p50": _nearest_rank(ordered, 0.50) / divisor,
        "p95": _nearest_rank(ordered, 0.95) / divisor,
        "max": max(ordered) / divisor,
    }


def summarize_timings(samples: tuple[TimingSample, ...]) -> dict[str, object]:
    """Summarize wall latency, CPU time, result size, and sequential throughput."""
    if not samples:
        raise ValueError("measurement samples must not be empty")
    wall = tuple(float(sample.wall_ns) for sample in samples)
    cpu = tuple(float(sample.cpu_ns) for sample in samples)
    sizes = tuple(float(sample.result_bytes) for sample in samples)
    total_wall_ns = sum(wall)
    return {
        "sample_count": len(samples),
        "percentile_method": "nearest_rank",
        "wall_latency_ms": _distribution(wall, 1_000_000),
        "cpu_time_ms": _distribution(cpu, 1_000_000),
        "result_json_bytes": _distribution(sizes, 1),
        "sequential_games_per_second": len(samples) * 1_000_000_000 / total_wall_ns,
        "illegal_action_count": sum(sample.illegal_actions for sample in samples),
    }


def summarize_memory(samples: tuple[MemorySample, ...]) -> dict[str, object]:
    """Summarize Python allocator peaks without claiming whole-process RSS."""
    if not samples:
        raise ValueError("measurement samples must not be empty")
    peaks = tuple(float(sample.peak_python_bytes) for sample in samples)
    return {
        "sample_count": len(samples),
        "metric": "tracemalloc_peak_python_allocations",
        "percentile_method": "nearest_rank",
        "peak_python_mib": _distribution(peaks, 1_048_576),
    }
