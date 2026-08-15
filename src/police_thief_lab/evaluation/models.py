"""Immutable records and aggregate shapes for local batch evaluation."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class GameResult:
    """Compact result and evaluator-only diagnostics for one local game."""

    seed: int
    scenario: str
    terminal_reason: str
    police_score: int
    thief_score: int
    thief_actions: int
    police_actions: int
    barriers_placed: int
    illegal_actions: int
    reachable_area_initial: int
    reachable_area_final: int
    separator_completed: int = 0
    wrong_side_cuts: int = 0
    unfinished_crossings: int = 0
    tactical_barriers_attempted: int = 0
    tactical_barrier_captures: int = 0
    tactical_area_reduction: int = 0
    tactical_unproductive_barriers: int = 0


@dataclass(frozen=True, slots=True)
class BatchResult:
    """Reproducible aggregate plus constituent game records."""

    police_policy: str
    thief_policy: str
    games: tuple[GameResult, ...]
    elapsed_seconds: float
    metrics: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        """Return a stable machine-readable representation."""
        return {
            "police_policy": self.police_policy,
            "thief_policy": self.thief_policy,
            "elapsed_seconds": self.elapsed_seconds,
            "metrics": self.metrics,
            "games": [asdict(game) for game in self.games],
        }
