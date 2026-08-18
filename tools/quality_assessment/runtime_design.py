"""Validation for the preregistered local runtime measurement design."""

from __future__ import annotations

import hashlib
import json
import subprocess
from dataclasses import dataclass
from pathlib import Path

_EXPECTED_CONFIG = {
    "barrier_placement_mode": "adjacent_only",
    "barrier_quota": 14,
    "blocked_cells": [],
    "board_size": 7,
    "police_start": [0, 0],
    "scent_profile": "subtractive_chebyshev_v1",
    "survival_threshold": 35,
    "thief_start": [3, 3],
    "turn_model": "reference_v3_alternating",
}


@dataclass(frozen=True, slots=True)
class MeasurementDesign:
    """Validated sample counts, seed ranges, policies, and source provenance."""

    scope: str
    police_policy: str
    thief_policy: str
    source_tree_sha: str
    design_sha256: str
    warmup_games: int
    warmup_seed_start: int
    timed_games: int
    timed_seed_start: int
    memory_games: int
    memory_seed_start: int


def _positive(data: dict[str, object], key: str) -> int:
    """Return a strictly positive, non-boolean integer design value."""
    value = data.get(key)
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise ValueError(f"design field {key} must be a positive integer")
    return value


def _source_tree(root: Path) -> str:
    """Return the exact Git tree identity of project production source."""
    result = subprocess.run(
        ["git", "rev-parse", "HEAD:src"], cwd=root, capture_output=True, text=True
    )
    if result.returncode != 0:
        raise ValueError("unable to resolve the tracked src tree")
    return result.stdout.strip()


def load_design(path: Path, repo_root: Path) -> MeasurementDesign:
    """Load an immutable historical design without rewriting its source identity."""
    raw = path.read_bytes()
    data = json.loads(raw.decode("utf-8"))
    required = {
        "schema": "runtime_measurement_design_v1",
        "status": "PREREGISTERED_BEFORE_MEASUREMENT",
        "scope": "LOCAL_SIMULATOR_EXPERIMENT",
        "percentile_method": "nearest_rank",
        "police_policy": "ScentTacticalPolice",
        "thief_policy": "ScentEvasionThief",
    }
    for key, expected in required.items():
        if data.get(key) != expected:
            raise ValueError(f"unsupported measurement design field: {key}")
    if data.get("game_config") != _EXPECTED_CONFIG:
        raise ValueError("measurement game_config does not match the pinned local profile")
    source_tree_sha = data.get("source_tree_sha")
    if not isinstance(source_tree_sha, str) or len(source_tree_sha) != 40:
        raise ValueError("source_tree_sha must be a full Git tree identity")
    if not repo_root.is_dir():
        raise ValueError("measurement repository root is unavailable")
    return MeasurementDesign(
        scope=data["scope"],
        police_policy=data["police_policy"],
        thief_policy=data["thief_policy"],
        source_tree_sha=source_tree_sha,
        design_sha256=hashlib.sha256(raw).hexdigest(),
        warmup_games=_positive(data, "warmup_games"),
        warmup_seed_start=_positive(data, "warmup_seed_start"),
        timed_games=_positive(data, "timed_games"),
        timed_seed_start=_positive(data, "timed_seed_start"),
        memory_games=_positive(data, "memory_games"),
        memory_seed_start=_positive(data, "memory_seed_start"),
    )


def require_current_source_tree(design: MeasurementDesign, repo_root: Path) -> None:
    """Block a new measurement when code differs from its preregistered source tree."""
    if _source_tree(repo_root) != design.source_tree_sha:
        raise ValueError("current src tree differs from the preregistered design")
