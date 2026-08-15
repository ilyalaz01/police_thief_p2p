"""Simple legal random, scent-pursuit, and space-preserving policies."""

from __future__ import annotations

import random

from ..models import Action, MoveType, Observation, Role
from .geometry import blocked, manhattan, reachable_area, target_of


class RandomLegalPolice:
    """Seeded uniform sampling from the Police legal-action list."""

    def __init__(self, seed: int) -> None:
        self._random = random.Random(seed)

    def choose_action(self, observation: Observation) -> Action:
        """Choose only an action supplied by the observation."""
        if observation.local.role is not Role.POLICE:
            raise ValueError("RandomLegalPolice requires a Police observation")
        return self._random.choice(observation.legal_actions)


class RandomLegalThief:
    """Seeded uniform sampling from the Thief legal-action list."""

    def __init__(self, seed: int) -> None:
        self._random = random.Random(seed)

    def choose_action(self, observation: Observation) -> Action:
        """Choose only an action supplied by the observation."""
        if observation.local.role is not Role.THIEF:
            raise ValueError("RandomLegalThief requires a Thief observation")
        return self._random.choice(observation.legal_actions)


class ScentGreedyPolice:
    """Move toward the strongest observable scent cell; use no hidden coordinates."""

    def __init__(self, seed: int) -> None:
        self._random = random.Random(seed)

    def choose_action(self, observation: Observation) -> Action:
        """Minimize distance to the hottest scent cell with seeded tie-breaking."""
        moves = [a for a in observation.legal_actions if a.move_type is not MoveType.BARRIER]
        if not observation.opponent_scent:
            return self._random.choice(moves)
        target = max(
            observation.opponent_scent,
            key=lambda item: (item[1], -item[0].row, -item[0].col),
        )[0]
        hottest_barrier = Action.barrier(target)
        if hottest_barrier in observation.legal_actions:
            return hottest_barrier
        distances = {
            action: manhattan(target_of(action, observation.local.own_position), target)
            for action in moves
        }
        best_distance = min(distances.values())
        best = [action for action in moves if distances[action] == best_distance]
        return self._random.choice(best)


class SpaceSeekingThief:
    """Prefer moves with large components and distance from public edges/bottlenecks."""

    def __init__(self, seed: int) -> None:
        self._random = random.Random(seed)

    def choose_action(self, observation: Observation) -> Action:
        """Maximize reachable space, then edge clearance, using seeded ties."""
        obstacles = blocked(observation)
        scored: list[tuple[tuple[int, int], Action]] = []
        for action in observation.legal_actions:
            position = target_of(action, observation.local.own_position)
            edge_clearance = min(
                position.row,
                position.col,
                observation.board_size - 1 - position.row,
                observation.board_size - 1 - position.col,
            )
            score = (reachable_area(position, observation.board_size, obstacles), edge_clearance)
            scored.append((score, action))
        best = max(score for score, _ in scored)
        return self._random.choice([action for score, action in scored if score == best])
