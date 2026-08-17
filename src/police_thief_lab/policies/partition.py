"""Experimental graph-separator Police with closed-wall and funnel variants."""

from __future__ import annotations

import random
from dataclasses import dataclass
from enum import Enum

from ..models import Action, MoveType, Observation, Position, Role
from .belief import scent_weights
from .geometry import blocked, manhattan, target_of


class SeparatorVariant(str, Enum):
    """The two intentionally simple Phase 2 construction variants."""

    CLOSED_WALL = "closed_wall"
    CONTROLLED_GAP = "controlled_gap"


@dataclass(frozen=True, slots=True)
class SeparatorPlan:
    """A public-board line cut and the cells the Police plans to fill."""

    axis: str
    index: int
    targets: tuple[Position, ...]
    gap: Position | None
    believed_low_side_mass: float


def plan_separator(observation: Observation, variant: SeparatorVariant) -> SeparatorPlan:
    """Choose a low-cost, approximately mass-balanced horizontal or vertical cut."""
    weights = scent_weights(observation)
    obstacles = blocked(observation)
    candidates: list[tuple[tuple[float, int, int, str], SeparatorPlan]] = []
    for axis in ("vertical", "horizontal"):
        for index in range(1, observation.board_size - 1):
            line = tuple(
                Position(row, index) if axis == "vertical" else Position(index, row)
                for row in range(observation.board_size)
            )
            open_cells = tuple(cell for cell in line if cell not in obstacles)
            gap = None
            if variant is SeparatorVariant.CONTROLLED_GAP and open_cells:
                gap = min(
                    open_cells,
                    key=lambda cell: manhattan(cell, observation.local.own_position),
                )
            targets = tuple(cell for cell in open_cells if cell != gap)
            low_mass = sum(
                weight
                for cell, weight in weights.items()
                if (cell.col < index if axis == "vertical" else cell.row < index)
            )
            balance = abs(0.5 - low_mass)
            plan = SeparatorPlan(axis, index, targets, gap, low_mass)
            candidates.append(((balance, len(targets), index, axis), plan))
    return min(candidates, key=lambda item: item[0])[1]


class PartitionPolice:
    """Build a public separator, otherwise move toward its nearest unfinished cell."""

    def __init__(self, seed: int, variant: SeparatorVariant = SeparatorVariant.CLOSED_WALL) -> None:
        """Initialize PartitionPolice with its validated setup values and private state."""
        self._random = random.Random(seed)
        self.variant = variant
        self.plan: SeparatorPlan | None = None
        self.plans_started = 0
        self.plans_completed = 0

    def choose_action(self, observation: Observation) -> Action:
        """Act using only the immutable Police observation and private plan memory."""
        if observation.local.role is not Role.POLICE:
            raise ValueError("PartitionPolice requires a Police observation")
        if self.plan is None:
            self.plan = plan_separator(observation, self.variant)
            self.plans_started += 1
        barrier_cells = {barrier.position for barrier in observation.barriers}
        pending = [cell for cell in self.plan.targets if cell not in barrier_cells]
        if not pending:
            self.plans_completed += 1
            self.plan = plan_separator(observation, self.variant)
            pending = [cell for cell in self.plan.targets if cell not in barrier_cells]
        if not pending:
            return self._pursue_scent(observation)
        legal_barriers = [
            action
            for action in observation.legal_actions
            if action.move_type is MoveType.BARRIER and action.barrier_position in pending
        ]
        if legal_barriers:
            return min(
                legal_barriers,
                key=lambda action: self.plan.targets.index(action.barrier_position),
            )
        moves = [
            action
            for action in observation.legal_actions
            if action.move_type is not MoveType.BARRIER
        ]
        target = min(pending, key=lambda cell: manhattan(cell, observation.local.own_position))
        distance_error = lambda action: abs(  # noqa: E731 - compact local scoring expression
            manhattan(target_of(action, observation.local.own_position), target) - 1
        )
        best_distance = min(distance_error(action) for action in moves)
        best = [action for action in moves if distance_error(action) == best_distance]
        return self._random.choice(best)

    def _pursue_scent(self, observation: Observation) -> Action:
        """Fallback when existing obstacles already complete the selected cut."""
        moves = [
            action
            for action in observation.legal_actions
            if action.move_type is not MoveType.BARRIER
        ]
        if not observation.opponent_scent:
            return self._random.choice(moves)
        target = max(observation.opponent_scent, key=lambda item: item[1])[0]
        distance = {
            action: manhattan(target_of(action, observation.local.own_position), target)
            for action in moves
        }
        best = min(distance.values())
        return self._random.choice([action for action in moves if distance[action] == best])
