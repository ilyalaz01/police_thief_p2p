"""Cross-play orchestration and JSON/Markdown rendering."""

from __future__ import annotations

import json
from collections.abc import Iterable, Mapping
from pathlib import Path

from ..models import GameConfig
from .models import BatchResult
from .runner import PolicyFactory, run_batch


def cross_play(
    configs: Iterable[tuple[str, GameConfig]],
    seeds: Iterable[int],
    police_policies: Mapping[str, PolicyFactory],
    thief_policies: Mapping[str, PolicyFactory],
) -> tuple[BatchResult, ...]:
    """Evaluate every Police × Thief pairing on identical scenarios and seeds."""
    config_set, seed_set = tuple(configs), tuple(seeds)
    return tuple(
        run_batch(config_set, seed_set, police_factory, thief_factory, police_name, thief_name)
        for police_name, police_factory in police_policies.items()
        for thief_name, thief_factory in thief_policies.items()
    )


def write_json(results: tuple[BatchResult, ...], path: Path) -> None:
    """Write machine-readable cross-play results once, after all in-memory games."""
    payload = {
        "total_games": sum(len(result.games) for result in results),
        "pairings": [result.to_dict() for result in results],
    }
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def markdown_matrix(results: tuple[BatchResult, ...]) -> str:
    """Render capture rates as a concise Police-row × Thief-column table."""
    police = list(dict.fromkeys(result.police_policy for result in results))
    thieves = list(dict.fromkeys(result.thief_policy for result in results))
    lookup = {(r.police_policy, r.thief_policy): r.metrics["capture_rate"] for r in results}
    lines = ["| Police \\ Thief | " + " | ".join(thieves) + " |", "|---|" + "---:|" * len(thieves)]
    for police_name in police:
        rates = [f"{lookup[police_name, thief_name]:.1%}" for thief_name in thieves]
        lines.append(f"| {police_name} | " + " | ".join(rates) + " |")
    return "\n".join(lines)
