"""Integration contracts for the local simulator measurement probe."""

from __future__ import annotations

import json

from tests.support.project_paths import PROJECT_ROOT
from tools.quality_assessment.runtime_models import MemorySample, TimingSample
from tools.quality_assessment.runtime_probe import execute_design, load_design, measure_one_game

DESIGN_PATH = PROJECT_ROOT / "data/quality/runtime_measurement_design.v1.json"
COST_DOC = PROJECT_ROOT / "docs/COST_AND_CAPACITY_ANALYSIS.md"
AUDIT_JSON = PROJECT_ROOT / "docs/audits/phase4d10_cost_capacity_measurements.json"
SAMPLES_JSON = PROJECT_ROOT / "docs/audits/phase4d10_runtime_samples.json"


def test_design_is_explicit_and_pinned_to_current_source_tree() -> None:
    """The preregistered design fixes scope, policies, samples, and source tree."""
    design = load_design(DESIGN_PATH, PROJECT_ROOT)
    assert design.scope == "LOCAL_SIMULATOR_EXPERIMENT"
    assert design.police_policy == "ScentTacticalPolice"
    assert design.thief_policy == "ScentEvasionThief"
    assert design.warmup_games == 20
    assert design.timed_games == 200
    assert design.memory_games == 30
    assert len(design.source_tree_sha) == 40


def test_execute_design_excludes_warmups_and_sorts_samples() -> None:
    """Uncounted warm-ups are called but absent from retained measurements."""
    seen: list[tuple[str, int]] = []

    def warmup(seed: int) -> None:
        seen.append(("warmup", seed))

    def timing(seed: int) -> TimingSample:
        seen.append(("timing", seed))
        return TimingSample(seed, seed, seed, 10, f"{seed:064x}", 0)

    def memory(seed: int) -> MemorySample:
        seen.append(("memory", seed))
        return MemorySample(seed, seed)

    design = load_design(DESIGN_PATH, PROJECT_ROOT)
    report = execute_design(design, warmup, timing, memory, {"python_version": "test"})
    assert len([kind for kind, _ in seen if kind == "warmup"]) == 20
    assert len(report["timing_samples"]) == 200
    assert len(report["memory_samples"]) == 30
    assert all(row["seed"] >= 60000 for row in report["timing_samples"])
    assert "59000" not in json.dumps(report)
    assert report["environment"] == {"python_version": "test"}


def test_real_probe_returns_scoped_local_measurements() -> None:
    """One real game yields positive local timing, memory, and result-size evidence."""
    timing, memory = measure_one_game(70000, include_memory=True)
    assert timing.wall_ns > 0
    assert timing.cpu_ns > 0
    assert timing.result_bytes > 0
    assert len(timing.result_sha256) == 64
    assert timing.illegal_actions == 0
    assert memory is not None and memory.peak_python_bytes > 0


def test_committed_evidence_closes_cost_without_vendor_invention() -> None:
    """Living docs retain measured facts and explicit monetary limitations."""
    payload = json.loads(AUDIT_JSON.read_text(encoding="utf-8"))
    text = COST_DOC.read_text(encoding="utf-8")
    assert payload["status"] == "GREEN"
    assert payload["operations"]["public_network_used"] is False
    assert payload["measurement"]["timing_samples"] == 200
    assert payload["measurement"]["memory_samples"] == 30
    assert "instrumented local simulator" in text
    assert "No vendor price or electricity cost was inferred" in text


def test_raw_measurements_recompute_the_committed_summary() -> None:
    """Retained samples and pure arithmetic independently reproduce the summary."""
    from tools.quality_assessment.runtime_models import summarize_memory, summarize_timings

    payload = json.loads(SAMPLES_JSON.read_text(encoding="utf-8"))
    timings = tuple(TimingSample(**row) for row in payload["timing_samples"])
    memories = tuple(MemorySample(**row) for row in payload["memory_samples"])
    assert payload["summary"]["timing"] == summarize_timings(timings)
    assert payload["summary"]["memory"] == summarize_memory(memories)
    assert {row.seed for row in timings}.isdisjoint(row.seed for row in memories)
    assert payload["summary"]["timing"]["illegal_action_count"] == 0


def test_new_runtime_measurement_python_files_stay_within_150_lines() -> None:
    """The measurement implementation preserves the governed file-size rule."""
    paths = (PROJECT_ROOT / "tools/quality_assessment").glob("runtime_*.py")
    violations: dict[str, int] = {}
    for path in paths:
        counted = sum(
            bool(line.strip()) and not line.lstrip().startswith("#")
            for line in path.read_text(encoding="utf-8").splitlines()
        )
        if counted > 150:
            violations[path.name] = counted
    assert violations == {}
