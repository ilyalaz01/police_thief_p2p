"""Bounded, network-free performance probe for the accepted local simulator."""

from __future__ import annotations

import hashlib
import json
import time
import tracemalloc
from collections.abc import Callable, Mapping
from dataclasses import asdict

from police_thief_lab import GameConfig
from police_thief_lab.evaluation import run_game
from police_thief_lab.policies import ScentEvasionThief, ScentTacticalPolice

from .runtime_design import MeasurementDesign, load_design
from .runtime_models import MemorySample, TimingSample, summarize_memory, summarize_timings

Warmup = Callable[[int], None]
TimingProbe = Callable[[int], TimingSample]
MemoryProbe = Callable[[int], MemorySample]


def _run(seed: int):
    """Run the exact preregistered local policy pairing once."""
    return run_game(
        GameConfig(), seed, ScentTacticalPolice, ScentEvasionThief, "default"
    )


def warmup_one_game(seed: int) -> None:
    """Execute one unretained local warm-up game."""
    _run(seed)


def measure_one_game(
    seed: int, *, include_memory: bool = False
) -> tuple[TimingSample, MemorySample | None]:
    """Measure one local game; optional memory is Python allocation peak only."""
    if include_memory and tracemalloc.is_tracing():
        raise RuntimeError("tracemalloc is already active")
    if include_memory:
        tracemalloc.start()
    wall_started = time.perf_counter_ns()
    cpu_started = time.process_time_ns()
    try:
        result = _run(seed)
        cpu_ns = time.process_time_ns() - cpu_started
        wall_ns = time.perf_counter_ns() - wall_started
        peak = tracemalloc.get_traced_memory()[1] if include_memory else None
    finally:
        if include_memory:
            tracemalloc.stop()
    body = json.dumps(asdict(result), sort_keys=True, separators=(",", ":")).encode()
    timing = TimingSample(
        seed=seed,
        wall_ns=wall_ns,
        cpu_ns=cpu_ns,
        result_bytes=len(body),
        result_sha256=hashlib.sha256(body).hexdigest(),
        illegal_actions=result.illegal_actions,
    )
    memory = MemorySample(seed, peak) if peak is not None else None
    return timing, memory


def timing_one_game(seed: int) -> TimingSample:
    """Return one timing sample without memory-tracing overhead."""
    return measure_one_game(seed)[0]


def memory_one_game(seed: int) -> MemorySample:
    """Return one separate tracemalloc sample; discard its distorted timing."""
    memory = measure_one_game(seed, include_memory=True)[1]
    if memory is None:  # pragma: no cover - guarded by include_memory
        raise RuntimeError("memory measurement was not produced")
    return memory


def execute_design(
    design: MeasurementDesign,
    warmup: Warmup,
    timing_probe: TimingProbe,
    memory_probe: MemoryProbe,
    environment: Mapping[str, object],
) -> dict[str, object]:
    """Execute fixed disjoint seed ranges and return retained measured evidence."""
    for seed in range(design.warmup_seed_start, design.warmup_seed_start + design.warmup_games):
        warmup(seed)
    timings = tuple(
        timing_probe(seed)
        for seed in range(design.timed_seed_start, design.timed_seed_start + design.timed_games)
    )
    memories = tuple(
        memory_probe(seed)
        for seed in range(design.memory_seed_start, design.memory_seed_start + design.memory_games)
    )
    return {
        "schema": "runtime_cost_capacity_measurement_v1",
        "status": "MEASURED",
        "scope": design.scope,
        "design_sha256": design.design_sha256,
        "source_tree_sha": design.source_tree_sha,
        "policies": {"police": design.police_policy, "thief": design.thief_policy},
        "environment": dict(environment),
        "timing_samples": [asdict(sample) for sample in sorted(timings, key=lambda row: row.seed)],
        "memory_samples": [asdict(sample) for sample in sorted(memories, key=lambda row: row.seed)],
        "summary": {
            "timing": summarize_timings(timings),
            "memory": summarize_memory(memories),
        },
    }


__all__ = [
    "execute_design",
    "load_design",
    "measure_one_game",
    "memory_one_game",
    "timing_one_game",
    "warmup_one_game",
]
