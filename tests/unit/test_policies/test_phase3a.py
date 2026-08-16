"""Phase 3A belief/search legality, isolation, budget, and determinism tests."""

from dataclasses import fields

import pytest

from police_thief_lab import Action, GameConfig, Observation, Role, Simulator, WorldState
from police_thief_lab.policies import (
    AggregationMode,
    BeliefSearchPolice,
    CurrentScentBelief,
    LookaheadEvasionThief,
    ScentTacticalPolice,
    TrajectoryBeamBelief,
)


def _police_observations() -> tuple[Observation, Observation]:
    simulator = Simulator(GameConfig())
    simulator.apply(Action.move(direction=_south()))
    first = simulator.observe(Role.POLICE)
    simulator.apply(Action.stay())
    simulator.apply(Action.stay())
    return first, simulator.observe(Role.POLICE)


def _south():
    from police_thief_lab import Direction

    return Direction.S


@pytest.mark.parametrize("estimator", [CurrentScentBelief(), TrajectoryBeamBelief(3, 32)])
def test_belief_interface_accepts_observation_without_hidden_truth(estimator) -> None:
    observation, _ = _police_observations()
    assert WorldState not in {type(observation), *(type(value) for value in fields(Observation))}
    estimator.update(observation)
    distribution = estimator.distribution()
    assert sum(distribution.values()) == pytest.approx(1)
    assert not hasattr(estimator, "world_state")
    assert not hasattr(estimator, "true_position")


def test_trajectory_expansion_obeys_moves_bounds_barriers_and_stay() -> None:
    first, second = _police_observations()
    estimator = TrajectoryBeamBelief(history_k=3, beam_width=128)
    estimator.update(first)
    estimator.update(second)
    obstacles = second.blocked_cells | frozenset(barrier.position for barrier in second.barriers)
    saw_stay = False
    for path in estimator.trajectories:
        assert all(
            0 <= cell.row < second.board_size
            and 0 <= cell.col < second.board_size
            and cell not in obstacles
            for cell in path
        )
        for left, right in zip(path, path[1:], strict=False):
            distance = abs(left.row - right.row) + abs(left.col - right.col)
            assert distance <= 1
            saw_stay |= distance == 0
    assert saw_stay


@pytest.mark.parametrize("mode", list(AggregationMode))
def test_search_is_deterministic_legal_and_budgeted(mode: AggregationMode) -> None:
    observation, _ = _police_observations()
    left = BeliefSearchPolice(7, TrajectoryBeamBelief(3, 32), mode, node_budget=19)
    right = BeliefSearchPolice(7, TrajectoryBeamBelief(3, 32), mode, node_budget=19)
    assert left.choose_action(observation) == right.choose_action(observation)
    assert left.choose_action(observation) in observation.legal_actions
    assert left.last_search_nodes <= 19


def test_evaluator_truth_cannot_reach_search_policy() -> None:
    policy = BeliefSearchPolice(1)
    assert set(vars(policy)).isdisjoint({"simulator", "evaluator", "world_state", "truth"})
    forbidden = {"opponent_position", "world_state", "truth_metrics"}
    assert {field.name for field in fields(Observation)}.isdisjoint(forbidden)


def test_lookahead_thief_is_seeded_and_legal() -> None:
    observation = Simulator(GameConfig()).observe(Role.THIEF)
    left, right = LookaheadEvasionThief(9), LookaheadEvasionThief(9)
    assert left.choose_action(observation) == right.choose_action(observation)
    assert left.choose_action(observation) in observation.legal_actions


def test_frozen_scent_tactical_regression() -> None:
    """Representative seeded action stream freezes the Phase 2.5 champion."""
    observation, _ = _police_observations()
    policy = ScentTacticalPolice(23)
    from police_thief_lab import Direction

    assert [policy.choose_action(observation) for _ in range(3)] == [
        Action.move(Direction.E),
        Action.move(Direction.S),
        Action.move(Direction.S),
    ]
