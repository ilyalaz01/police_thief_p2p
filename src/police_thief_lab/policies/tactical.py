"""Direct scent pursuit with sparse, immediately valuable tactical barriers."""

from __future__ import annotations

import random

from ..models import Action, MoveType, Observation, Role
from .geometry import blocked, manhattan, neighbours, reachable_area, target_of


class ScentTacticalPolice:
    """Pursue scent, placing only adjacent high-confidence confinement barriers."""

    def __init__(self, seed: int) -> None:
        self._random = random.Random(seed)
        self.barriers_attempted = 0
        self.unproductive_barriers = 0
        self.area_reduction_from_barriers = 0

    def choose_action(self, observation: Observation) -> Action:
        """Use a barrier only at hot low-degree cells; otherwise chase scent."""
        if observation.local.role is not Role.POLICE:
            raise ValueError("ScentTacticalPolice requires a Police observation")
        scent = dict(observation.opponent_scent)
        obstacles = blocked(observation)
        candidates = []
        for action in observation.legal_actions:
            if action.move_type is not MoveType.BARRIER:
                continue
            cell = action.barrier_position
            intensity = scent.get(cell, 0.0)
            degree = len(neighbours(cell, observation.board_size, obstacles))
            before = reachable_area(cell, observation.board_size, obstacles)
            after = reachable_area(
                observation.local.own_position,
                observation.board_size,
                obstacles | {cell},
            )
            value = (intensity, 4 - degree, before - after)
            if intensity >= 0.7 or (intensity >= 0.5 and degree <= 2):
                candidates.append((value, action, max(0, before - after)))
        if candidates and observation.local.own_barriers_placed < 5:
            best_value = max(value for value, _, _ in candidates)
            choices = [
                (action, reduction)
                for value, action, reduction in candidates
                if value == best_value
            ]
            action, reduction = self._random.choice(choices)
            self.barriers_attempted += 1
            self.area_reduction_from_barriers += reduction
            self.unproductive_barriers += reduction == 0
            return action
        return self._pursue(observation)

    def _pursue(self, observation: Observation) -> Action:
        moves = [
            action
            for action in observation.legal_actions
            if action.move_type is not MoveType.BARRIER
        ]
        if not observation.opponent_scent:
            return self._random.choice(moves)
        target = max(observation.opponent_scent, key=lambda item: item[1])[0]
        distances = {
            action: manhattan(target_of(action, observation.local.own_position), target)
            for action in moves
        }
        best = min(distances.values())
        return self._random.choice([action for action in moves if distances[action] == best])
