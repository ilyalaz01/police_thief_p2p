"""Deterministic, observation-only search diagnostics introduced in Phase 3B."""

from __future__ import annotations

import random
import time
from dataclasses import dataclass
from enum import Enum

from ..models import Action, Direction, MoveType, Observation, Position, Role
from ..scent import ReferenceSubtractiveChebyshevV1
from .belief import BeliefEstimator, CurrentScentBelief
from .geometry import blocked, manhattan, neighbours, reachable_area, target_of


class OpponentModel(str, Enum):
    """Legally reconstructible deterministic Thief response models."""

    SIMPLE_EVASION = "simple_evasion"
    SCENT_EVASION_MODEL = "scent_evasion_model"
    LOOKAHEAD_EVASION_MODEL = "lookahead_evasion_model"


class BeliefUsage(str, Enum):
    """Controlled ways of consuming an existing belief marginal."""

    HOTTEST_CELL = "hottest_cell"
    TOP3_WEIGHTED = "top3_weighted"
    FULL = "full"


FEATURES = (
    "distance_pursuit",
    "capture_probability",
    "reachable_area_reduction",
    "opponent_mobility",
    "police_mobility",
    "barrier_cost",
    "bottleneck_separator",
    "self_isolation_risk",
    "survival_horizon_urgency",
)


@dataclass(frozen=True, slots=True)
class ActionDiagnostic:
    """Truth-free explanation of a scored root action."""

    action: Action
    score: float
    components: dict[str, float]
    modeled_replies: tuple[Position, ...]


class DeterministicSearchPolice:
    """Small repaired search with explicit belief, reply model, depth, and ablations."""

    def __init__(
        self,
        seed: int,
        belief: BeliefEstimator | None = None,
        opponent_model: OpponentModel = OpponentModel.LOOKAHEAD_EVASION_MODEL,
        belief_usage: BeliefUsage = BeliefUsage.HOTTEST_CELL,
        depth: int = 2,
        disabled_features: frozenset[str] = frozenset(),
        node_budget: int = 512,
    ) -> None:
        if depth not in (1, 2, 3) or node_budget < 1:
            raise ValueError("depth must be 1..3 and node_budget must be positive")
        unknown = disabled_features - frozenset(FEATURES)
        if unknown:
            raise ValueError(f"unknown disabled features: {sorted(unknown)}")
        self._random = random.Random(seed)
        self.belief = belief or CurrentScentBelief()
        self.opponent_model = opponent_model
        self.belief_usage = belief_usage
        self.depth = depth
        self.disabled_features = disabled_features
        self.node_budget = node_budget
        self.search_nodes_evaluated = 0
        self.last_search_nodes = 0
        self.decision_times: list[float] = []
        self.last_diagnostics: tuple[ActionDiagnostic, ...] = ()
        self._own_scent: tuple[tuple[Position, float], ...] = ()
        self._scent_model = ReferenceSubtractiveChebyshevV1()

    def choose_action(self, observation: Observation) -> Action:
        if observation.local.role is not Role.POLICE:
            raise ValueError("DeterministicSearchPolice requires a Police observation")
        started = time.perf_counter()
        self.belief.update(observation)
        states = self._states(self.belief.distribution())
        self.last_search_nodes = 0
        rows = []
        for action in observation.legal_actions:
            weighted = []
            reply_union: set[Position] = set()
            component_totals = dict.fromkeys(FEATURES, 0.0)
            for thief, probability in states:
                value, components, replies = self._value(observation, action, thief)
                weighted.append((probability, value))
                reply_union.update(replies)
                for name, amount in components.items():
                    component_totals[name] += probability * amount
            mass = sum(weight for weight, _ in weighted)
            score = sum(weight * value for weight, value in weighted) / mass
            components = {name: value / mass for name, value in component_totals.items()}
            rows.append(ActionDiagnostic(action, score, components, tuple(sorted(reply_union))))
        best = max(row.score for row in rows)
        choice = self._random.choice([row.action for row in rows if row.score == best])
        self.last_diagnostics = tuple(rows)
        self.search_nodes_evaluated += self.last_search_nodes
        self.decision_times.append(time.perf_counter() - started)
        # This is the scent the next hypothetical/real Thief observes.
        police = target_of(choice, observation.local.own_position)
        self._own_scent = self._scent_model.advance(self._own_scent, police, observation.board_size)
        return choice

    def _states(self, distribution: dict[Position, float]) -> tuple[tuple[Position, float], ...]:
        ordered = sorted(distribution.items(), key=lambda item: (-item[1], item[0]))
        if self.belief_usage is BeliefUsage.HOTTEST_CELL:
            return ((ordered[0][0], 1.0),)
        if self.belief_usage is BeliefUsage.TOP3_WEIGHTED:
            return tuple(ordered[:3])
        return tuple(ordered)

    def _value(
        self, observation: Observation, action: Action, thief: Position
    ) -> tuple[float, dict[str, float], tuple[Position, ...]]:
        if self.last_search_nodes >= self.node_budget:
            return -1000.0, dict.fromkeys(FEATURES, 0.0), ()
        obstacles = blocked(observation)
        police = target_of(action, observation.local.own_position)
        barrier = action.barrier_position if action.move_type is MoveType.BARRIER else None
        after = obstacles | ({barrier} if barrier is not None else set())
        # Phase 3A's critical bug was checking capture only after a reply.
        if police == thief or barrier == thief:
            components = dict.fromkeys(FEATURES, 0.0)
            components["capture_probability"] = 100.0
            return self._sum(components), components, ()
        leaf_scent = self._scent_model.advance(self._own_scent, police, observation.board_size)
        replies = (
            ()
            if self.depth == 1
            else modeled_replies(
                self.opponent_model,
                thief,
                police,
                observation.board_size,
                frozenset(after),
                leaf_scent,
            )
        )
        candidates = replies or (thief,)
        evaluated = []
        for reply in candidates:
            if self.last_search_nodes >= self.node_budget:
                break
            self.last_search_nodes += 1
            components = self._components(observation, police, thief, reply, barrier, after)
            value = self._sum(components)
            if self.depth == 3:
                next_values = [
                    self._simple_next_police_value(observation, candidate, reply, after)
                    for candidate in _hypothetical_police_actions(
                        police,
                        observation.board_size,
                        frozenset(after),
                        observation.local.own_barriers_placed + int(barrier is not None),
                        observation.barrier_quota,
                    )
                ]
                value = max(next_values)
            evaluated.append((value, components))
        if not evaluated:
            components = dict.fromkeys(FEATURES, 0.0)
            return -1000.0, components, replies
        value, components = min(evaluated, key=lambda item: item[0])
        return value, components, replies

    def _components(self, observation, police, old_thief, thief, barrier, obstacles):
        old_area = reachable_area(old_thief, observation.board_size, blocked(observation))
        thief_area = reachable_area(thief, observation.board_size, frozenset(obstacles))
        thief_exits = len(neighbours(thief, observation.board_size, frozenset(obstacles)))
        police_area = reachable_area(police, observation.board_size, frozenset(obstacles))
        police_exits = len(neighbours(police, observation.board_size, frozenset(obstacles)))
        separated = police_area != thief_area
        horizon = max(0, 35 - observation.local.own_moves)
        return {
            "distance_pursuit": -3.0 * manhattan(police, thief),
            "capture_probability": 100.0 * (police == thief),
            "reachable_area_reduction": 0.12 * (old_area - thief_area),
            "opponent_mobility": -0.7 * thief_exits,
            "police_mobility": 0.35 * police_exits,
            "barrier_cost": -1.2 * (barrier is not None),
            "bottleneck_separator": 0.5 * (4 - thief_exits),
            "self_isolation_risk": -6.0 * separated,
            "survival_horizon_urgency": -0.2 * (35 - horizon) / 35,
        }

    def _simple_next_police_value(self, observation, action, thief, obstacles):
        police = target_of(action, observation.local.own_position)
        barrier = action.barrier_position if action.move_type is MoveType.BARRIER else None
        if police == thief or barrier == thief:
            return 100.0 if "capture_probability" not in self.disabled_features else 0.0
        after = obstacles | ({barrier} if barrier is not None else set())
        return self._sum(self._components(observation, police, thief, thief, barrier, after))

    def _sum(self, components: dict[str, float]) -> float:
        return sum(
            value for name, value in components.items() if name not in self.disabled_features
        )


class TacticalOneStepPolice:
    """One Police action followed by a leaf score distilled from the frozen champion."""

    def __init__(self, seed: int) -> None:
        self._random = random.Random(seed)
        self.search_nodes_evaluated = 0
        self.last_search_nodes = 0
        self.decision_times: list[float] = []
        self.last_diagnostics: tuple[ActionDiagnostic, ...] = ()

    def choose_action(self, observation: Observation) -> Action:
        if observation.local.role is not Role.POLICE:
            raise ValueError("TacticalOneStepPolice requires a Police observation")
        started = time.perf_counter()
        scent = dict(observation.opponent_scent)
        target = max(observation.opponent_scent, key=lambda item: item[1])[0]
        obstacles = blocked(observation)
        rows = []
        for action in observation.legal_actions:
            self.search_nodes_evaluated += 1
            self.last_search_nodes += 1
            if action.move_type is MoveType.BARRIER:
                cell = action.barrier_position
                degree = len(neighbours(cell, observation.board_size, obstacles))
                before = reachable_area(cell, observation.board_size, obstacles)
                after = reachable_area(
                    observation.local.own_position, observation.board_size, obstacles | {cell}
                )
                eligible = scent.get(cell, 0.0) >= 0.7 or (
                    scent.get(cell, 0.0) >= 0.5 and degree <= 2
                )
                score = (
                    1_000_000.0 * eligible
                    + 10_000 * scent.get(cell, 0.0)
                    + 100 * (4 - degree)
                    + before
                    - after
                )
                if not eligible:
                    score = -1000.0
                if observation.local.own_barriers_placed >= 5:
                    score = -1000.0
            else:
                destination = target_of(action, observation.local.own_position)
                score = -manhattan(destination, target)
            rows.append(ActionDiagnostic(action, score, {}, ()))
        best = max(row.score for row in rows)
        choice = self._random.choice([row.action for row in rows if row.score == best])
        self.last_diagnostics = tuple(rows)
        self.decision_times.append(time.perf_counter() - started)
        return choice


def modeled_replies(model, thief, police, size, obstacles, police_scent):
    """Return all top-ranked replies; randomness in frozen policies is represented as ties."""
    cells = (*neighbours(thief, size, obstacles), thief)
    if model is OpponentModel.SIMPLE_EVASION:
        scores = {
            cell: (manhattan(cell, police), len(neighbours(cell, size, obstacles)))
            for cell in cells
        }
    elif model is OpponentModel.SCENT_EVASION_MODEL:
        scent = dict(police_scent)
        scores = {
            cell: (
                -scent.get(cell, 0.0),
                reachable_area(cell, size, obstacles),
                len(neighbours(cell, size, obstacles)),
                min(cell.row, cell.col, size - 1 - cell.row, size - 1 - cell.col),
            )
            for cell in cells
        }
    else:
        scent = dict(police_scent)
        scores = {}
        for cell in cells:
            future = []
            for next_cell in (*neighbours(cell, size, obstacles), cell):
                exits = neighbours(next_cell, size, obstacles)
                independent = len(
                    {
                        candidate
                        for exit_cell in exits
                        for candidate in neighbours(exit_cell, size, obstacles)
                    }
                )
                future.append(
                    (
                        -scent.get(next_cell, 0.0),
                        reachable_area(next_cell, size, obstacles),
                        len(exits),
                        independent,
                        -int(len(exits) <= 1),
                    )
                )
            scores[cell] = min(future)
    best = max(scores.values())
    return tuple(cell for cell in cells if scores[cell] == best)


def _hypothetical_police_actions(position, size, obstacles, placed, quota):
    directions = (Direction.N, Direction.S, Direction.E, Direction.W)
    moves = tuple(
        Action.move(direction)
        for direction, cell in zip(
            directions,
            (
                Position(position.row - 1, position.col),
                Position(position.row + 1, position.col),
                Position(position.row, position.col + 1),
                Position(position.row, position.col - 1),
            ),
            strict=True,
        )
        if cell in neighbours(position, size, obstacles)
    )
    barriers = (
        tuple(Action.barrier(cell) for cell in neighbours(position, size, obstacles))
        if placed < quota
        else ()
    )
    return (*moves, Action.stay(), *barriers)
