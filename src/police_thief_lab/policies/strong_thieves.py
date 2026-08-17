"""Stronger observation-only Thief baselines for adversarial validation."""

from __future__ import annotations

import random

from ..models import Action, Observation, Role
from .geometry import blocked, neighbours, reachable_area, target_of


class ScentEvasionThief:
    """Avoid Police scent while preserving space and interior clearance."""

    def __init__(self, seed: int) -> None:
        """Initialize ScentEvasionThief with its validated setup values and private state."""
        self._random = random.Random(seed)

    def choose_action(self, observation: Observation) -> Action:
        """Maximize a lexicographic observable safety score."""
        _require_thief(observation)
        obstacles, scent = blocked(observation), dict(observation.opponent_scent)
        scored = []
        for action in observation.legal_actions:
            cell = target_of(action, observation.local.own_position)
            clearance = min(
                cell.row,
                cell.col,
                observation.board_size - 1 - cell.row,
                observation.board_size - 1 - cell.col,
            )
            score = (
                -scent.get(cell, 0.0),
                reachable_area(cell, observation.board_size, obstacles),
                len(neighbours(cell, observation.board_size, obstacles)),
                clearance,
            )
            scored.append((score, action))
        best = max(score for score, _ in scored)
        return self._random.choice([action for score, action in scored if score == best])


class BarrierAwareThief:
    """Favor cells with multiple exits and low enclosure vulnerability."""

    def __init__(self, seed: int) -> None:
        """Initialize BarrierAwareThief with its validated setup values and private state."""
        self._random = random.Random(seed)

    def choose_action(self, observation: Observation) -> Action:
        """Prefer independent public escape routes, space, then low Police scent."""
        _require_thief(observation)
        obstacles, scent = blocked(observation), dict(observation.opponent_scent)
        scored = []
        for action in observation.legal_actions:
            cell = target_of(action, observation.local.own_position)
            exits = neighbours(cell, observation.board_size, obstacles)
            second_order = len(
                {
                    next_cell
                    for exit_cell in exits
                    for next_cell in neighbours(exit_cell, observation.board_size, obstacles)
                }
            )
            score = (
                len(exits),
                second_order,
                reachable_area(cell, observation.board_size, obstacles),
                -scent.get(cell, 0.0),
            )
            scored.append((score, action))
        best = max(score for score, _ in scored)
        return self._random.choice([action for score, action in scored if score == best])


class LookaheadEvasionThief:
    """Two-step local evasion using only public graph and observed Police scent."""

    def __init__(self, seed: int) -> None:
        """Initialize LookaheadEvasionThief with its validated setup values and private state."""
        self._random = random.Random(seed)

    def choose_action(self, observation: Observation) -> Action:
        """Maximize worst next-step safety with seeded tie-breaking."""
        _require_thief(observation)
        obstacles, scent = blocked(observation), dict(observation.opponent_scent)
        scored = []
        for action in observation.legal_actions:
            cell = target_of(action, observation.local.own_position)
            continuations = (*neighbours(cell, observation.board_size, obstacles), cell)
            future = []
            for next_cell in continuations:
                exits = neighbours(next_cell, observation.board_size, obstacles)
                independent = len(
                    {
                        candidate
                        for exit_cell in exits
                        for candidate in neighbours(exit_cell, observation.board_size, obstacles)
                    }
                )
                edge_danger = int(len(exits) <= 1)
                future.append(
                    (
                        -scent.get(next_cell, 0.0),
                        reachable_area(next_cell, observation.board_size, obstacles),
                        len(exits),
                        independent,
                        -edge_danger,
                    )
                )
            score = min(future)
            scored.append((score, action))
        best = max(score for score, _ in scored)
        return self._random.choice([action for score, action in scored if score == best])


def _require_thief(observation: Observation) -> None:
    """Compute the internal require thief step used by module."""
    if observation.local.role is not Role.THIEF:
        raise ValueError("Thief policy requires a Thief observation")
