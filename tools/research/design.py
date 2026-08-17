"""Load the preregistered design and map it to public SDK inputs."""

from __future__ import annotations

import json
from collections.abc import Iterator
from pathlib import Path
from typing import Any

from police_thief_lab import PoliceThiefSDK

SDK = PoliceThiefSDK()
SCHEMA = "police_thief_sensitivity_design_v1"


def load_design(path: Path) -> dict[str, Any]:
    """Load and validate the bounded preregistered sensitivity design."""
    value = json.loads(path.read_text(encoding="utf-8"))
    if value.get("_schema") != SCHEMA:
        raise ValueError("unsupported sensitivity design schema")
    if value.get("status") != "PREDECLARED_BEFORE_FIRST_RUN":
        raise ValueError("sensitivity design is not preregistered")
    if value.get("operation_class") != "LOCAL_SIMULATOR_EXPERIMENT":
        raise ValueError("only a local simulator experiment is supported")
    seeds = value.get("seeds", {})
    if seeds != {"start": 0, "stop_exclusive": 40}:
        raise ValueError("unexpected paired-seed range")
    expected = (
        len(value["settings"])
        * len(value["scenarios"])
        * len(value["policies"]["police"])
        * len(value["policies"]["thief"])
        * (seeds["stop_exclusive"] - seeds["start"])
    )
    if expected != value.get("expected_games"):
        raise ValueError("expected game count does not match the design")
    return value


def iter_cases(design: dict[str, Any]) -> Iterator[tuple[dict[str, Any], dict[str, Any], int]]:
    """Yield settings, scenarios, and paired seeds in declared order."""
    seeds = range(design["seeds"]["start"], design["seeds"]["stop_exclusive"])
    for setting in design["settings"]:
        for scenario in design["scenarios"]:
            for seed in seeds:
                yield setting, scenario, seed


def game_config(setting: dict[str, Any], scenario: dict[str, Any]):
    """Build one existing GameConfig from declared parameter and start tokens."""
    size = setting["board_size"]
    coordinates = {"zero": 0, "mid": size // 2, "last": size - 1}
    position = SDK.domain.Position
    police = position(*(coordinates[item] for item in scenario["police_start"]))
    thief = position(*(coordinates[item] for item in scenario["thief_start"]))
    return SDK.domain.GameConfig(
        board_size=size,
        police_start=police,
        thief_start=thief,
        survival_threshold=setting["survival_threshold"],
    )


def policy_factories(design: dict[str, Any]):
    """Resolve only the four preregistered existing policies through the SDK."""
    police = {
        "ScentTacticalPolice": SDK.policies.ScentTacticalPolice,
        "ScentGreedyPolice": SDK.policies.ScentGreedyPolice,
    }
    thief = {
        "BarrierAwareThief": SDK.policies.BarrierAwareThief,
        "ScentEvasionThief": SDK.policies.ScentEvasionThief,
    }
    requested_police = design["policies"]["police"]
    requested_thief = design["policies"]["thief"]
    if set(requested_police) != set(police) or set(requested_thief) != set(thief):
        raise ValueError("design requested an unapproved policy")
    return police, thief
