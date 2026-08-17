"""Pure contracts for bounded local runtime cost and capacity measurements."""

from __future__ import annotations

from tools.quality_assessment.runtime_models import (
    MemorySample,
    TimingSample,
    summarize_memory,
    summarize_timings,
)


def _timing(seed: int, wall_ms: int, cpu_ms: int, size: int = 100) -> TimingSample:
    return TimingSample(
        seed=seed,
        wall_ns=wall_ms * 1_000_000,
        cpu_ns=cpu_ms * 1_000_000,
        result_bytes=size,
        result_sha256=f"{seed:064x}",
        illegal_actions=0,
    )


def test_timing_summary_uses_declared_nearest_rank_percentiles() -> None:
    """P50/P95 and throughput use explicit, reviewable arithmetic."""
    samples = tuple(_timing(seed, seed, seed // 2) for seed in range(1, 21))
    summary = summarize_timings(samples)
    assert summary["wall_latency_ms"]["p50"] == 10.0
    assert summary["wall_latency_ms"]["p95"] == 19.0
    assert summary["wall_latency_ms"]["max"] == 20.0
    assert summary["cpu_time_ms"]["p50"] == 5.0
    assert summary["sequential_games_per_second"] == 1000 / 10.5
    assert summary["illegal_action_count"] == 0


def test_memory_summary_labels_python_allocator_peak() -> None:
    """Memory evidence stays scoped to tracemalloc, not whole-process RSS."""
    samples = tuple(
        MemorySample(seed=seed, peak_python_bytes=seed * 1_048_576)
        for seed in range(1, 21)
    )
    summary = summarize_memory(samples)
    assert summary["metric"] == "tracemalloc_peak_python_allocations"
    assert summary["peak_python_mib"]["p50"] == 10.0
    assert summary["peak_python_mib"]["p95"] == 19.0
    assert summary["peak_python_mib"]["max"] == 20.0


def test_empty_sample_sets_are_refused() -> None:
    """A report cannot silently claim capacity without observations."""
    for summarizer in (summarize_timings, summarize_memory):
        try:
            summarizer(())
        except ValueError as exc:
            assert str(exc) == "measurement samples must not be empty"
        else:
            raise AssertionError("empty measurements were accepted")
