"""Small uncertainty-aware tactical graph search for Phase 3A."""

from __future__ import annotations

import random
import statistics
import time
from enum import Enum

from ..models import Action, MoveType, Observation, Position, Role
from .belief import BeliefEstimator, CurrentScentBelief
from .geometry import blocked, manhattan, neighbours, reachable_area, target_of


class AggregationMode(str, Enum):
    """How plausible hidden-state action values are combined."""

    EXPECTED = "expected"
    ROBUST = "robust"


class BeliefSearchPolice:
    """Bounded two-ply search over a belief marginal and local Thief replies."""

    def __init__(
        self,
        seed: int,
        belief: BeliefEstimator | None = None,
        aggregation: AggregationMode = AggregationMode.EXPECTED,
        node_budget: int = 256,
        plausible_states: int = 12,
    ) -> None:
        if node_budget < 1 or plausible_states < 1:
            raise ValueError("search budgets must be positive")
        self._random = random.Random(seed)
        self.belief = belief or CurrentScentBelief()
        self.aggregation = aggregation
        self.node_budget = node_budget
        self.plausible_states = plausible_states
        self.search_nodes_evaluated = 0
        self.last_search_nodes = 0
        self.decision_times: list[float] = []
        self.belief_update_times: list[float] = []

    def choose_action(self, observation: Observation) -> Action:
        if observation.local.role is not Role.POLICE:
            raise ValueError("BeliefSearchPolice requires a Police observation")
        started = time.perf_counter()
        self.belief.update(observation)
        self.belief_update_times.append(self.belief.diagnostics().last_update_seconds)
        states = sorted(self.belief.distribution().items(), key=lambda item: -item[1])[
            : self.plausible_states
        ]
        self.last_search_nodes = 0
        scored = []
        for action in observation.legal_actions:
            if self.last_search_nodes >= self.node_budget:
                break
            outcomes = []
            for thief_cell, probability in states:
                if self.last_search_nodes >= self.node_budget:
                    break
                outcomes.append((probability, self._state_value(observation, action, thief_cell)))
            if outcomes:
                expected = sum(weight * value for weight, value in outcomes) / sum(
                    weight for weight, _ in outcomes
                )
                if self.aggregation is AggregationMode.ROBUST:
                    tail = statistics.fmean(sorted(value for _, value in outcomes)[:3])
                    expected = 0.75 * expected + 0.25 * tail
                scored.append((expected, action))
        self.search_nodes_evaluated += self.last_search_nodes
        best = max(score for score, _ in scored)
        choice = self._random.choice([action for score, action in scored if score == best])
        self.decision_times.append(time.perf_counter() - started)
        return choice

    def _state_value(self, observation: Observation, action: Action, thief: Position) -> float:
        obstacles = blocked(observation)
        police = target_of(action, observation.local.own_position)
        barrier = action.barrier_position if action.move_type is MoveType.BARRIER else None
        after = obstacles | ({barrier} if barrier is not None else set())
        replies = (*neighbours(thief, observation.board_size, frozenset(after)), thief)
        reply_values = []
        for reply in replies:
            if self.last_search_nodes >= self.node_budget:
                break
            self.last_search_nodes += 1
            capture = 1.0 if police == reply or barrier == reply else 0.0
            thief_area = reachable_area(reply, observation.board_size, frozenset(after))
            thief_exits = len(neighbours(reply, observation.board_size, frozenset(after)))
            police_exits = len(neighbours(police, observation.board_size, frozenset(after)))
            degree_bonus = 4 - thief_exits
            separation_risk = (
                1.0
                if thief_area
                and reachable_area(police, observation.board_size, frozenset(after)) != thief_area
                else 0.0
            )
            barrier_cost = 1.0 if barrier is not None else 0.0
            time_pressure = observation.local.own_moves / 35
            value = (
                100 * capture
                - 3 * manhattan(police, reply)
                - 0.12 * thief_area
                - 0.7 * thief_exits
                + 0.35 * police_exits
                + 0.5 * degree_bonus
                - 1.2 * barrier_cost
                - 6 * separation_risk
                - 0.2 * time_pressure
            )
            reply_values.append(value)
        # Thief continuation is adversarial at the shallow second ply.
        return min(reply_values) if reply_values else -1000.0
