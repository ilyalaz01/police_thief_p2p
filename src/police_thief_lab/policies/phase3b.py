"""Deterministic, observation-only search diagnostics introduced in Phase 3B."""

from __future__ import annotations

import random
import time

from ..models import Action, MoveType, Observation, Position, Role
from ..scent import ReferenceSubtractiveChebyshevV1
from .belief import BeliefEstimator, CurrentScentBelief
from .geometry import blocked, manhattan, neighbours, reachable_area, target_of
from .phase3b_models import FEATURES, ActionDiagnostic, BeliefUsage, OpponentModel
from .phase3b_replies import (
    _hypothetical_police_actions as _hypothetical_police_actions,
)
from .phase3b_replies import modeled_replies as modeled_replies
from .phase3b_scoring import _SearchScoringMixin


class DeterministicSearchPolice(_SearchScoringMixin):
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
        """Initialize search depth, model, belief mode, and bounded node budget."""
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
        """Choose a deterministic legal action using only the supplied role-local observation."""
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
        """Compute the internal states step used by DeterministicSearchPolice."""
        ordered = sorted(distribution.items(), key=lambda item: (-item[1], item[0]))
        if self.belief_usage is BeliefUsage.HOTTEST_CELL:
            return ((ordered[0][0], 1.0),)
        if self.belief_usage is BeliefUsage.TOP3_WEIGHTED:
            return tuple(ordered[:3])
        return tuple(ordered)

class TacticalOneStepPolice:
    """One Police action followed by a leaf score distilled from the frozen champion."""

    def __init__(self, seed: int) -> None:
        """Initialize TacticalOneStepPolice with its validated setup values and private state."""
        self._random = random.Random(seed)
        self.search_nodes_evaluated = 0
        self.last_search_nodes = 0
        self.decision_times: list[float] = []
        self.last_diagnostics: tuple[ActionDiagnostic, ...] = ()

    def choose_action(self, observation: Observation) -> Action:
        """Choose a deterministic legal action using only the supplied role-local observation."""
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
