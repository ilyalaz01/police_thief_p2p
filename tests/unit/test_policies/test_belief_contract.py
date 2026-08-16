"""Characterization of the Phase 3A observation-only belief contract."""

import hashlib
import inspect
import json
from dataclasses import fields, replace

import pytest

from police_thief_lab import (
    Action,
    Direction,
    GameConfig,
    Observation,
    Role,
    Simulator,
    WorldState,
    policies,
)
from police_thief_lab.models import Position
from police_thief_lab.policies.belief import (
    BeliefDiagnostics,
    BeliefEstimator,
    CurrentScentBelief,
    TrajectoryBeamBelief,
    scent_weights,
)


def _observations() -> tuple[Observation, Observation]:
    simulator = Simulator(GameConfig())
    simulator.apply(Action.move(Direction.S))
    first = simulator.observe(Role.POLICE)
    simulator.apply(Action.stay())
    simulator.apply(Action.stay())
    return first, simulator.observe(Role.POLICE)


def _distribution_vector(distribution: dict[Position, float]) -> list:
    return [
        [[position.row, position.col], value] for position, value in sorted(distribution.items())
    ]


def _trajectory_vector(trajectories: tuple[tuple[Position, ...], ...]) -> list:
    return [[[position.row, position.col] for position in path] for path in trajectories]


def _digest(value: object) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest()


def test_public_imports_signatures_defaults_and_exports_are_characterized() -> None:
    assert str(inspect.signature(CurrentScentBelief)) == "() -> 'None'"
    assert str(inspect.signature(TrajectoryBeamBelief)) == (
        "(history_k: 'int' = 6, beam_width: 'int' = 128) -> 'None'"
    )
    assert str(inspect.signature(scent_weights)) == (
        "(observation: 'Observation') -> 'dict[Position, float]'"
    )
    assert BeliefDiagnostics.__name__ == "BeliefDiagnostics"
    assert BeliefEstimator.__name__ == "BeliefEstimator"
    assert policies.__all__ == [
        "PartitionPolice",
        "BarrierAwareThief",
        "BeliefEstimator",
        "BeliefSearchPolice",
        "BeliefUsage",
        "CurrentScentBelief",
        "AggregationMode",
        "LookaheadEvasionThief",
        "DeterministicSearchPolice",
        "OpponentModel",
        "RandomLegalPolice",
        "RandomLegalThief",
        "ScentGreedyPolice",
        "ScentEvasionThief",
        "ScentTacticalPolice",
        "SeparatorPlan",
        "SeparatorVariant",
        "SpaceSeekingThief",
        "TrajectoryBeamBelief",
        "TacticalOneStepPolice",
        "plan_separator",
    ]


def test_current_scent_positive_empty_copy_and_compatibility_vectors() -> None:
    positive, _ = _observations()
    empty = replace(positive, opponent_scent=())
    estimator = CurrentScentBelief()
    estimator.update(positive)
    distribution = estimator.distribution()
    assert sum(distribution.values()) == pytest.approx(1)
    assert _digest(_distribution_vector(distribution)) == (
        "815223cd2f4dd8c6d2e51fac2ce1879f04ec05733af1f2d4642840dcfde422aa"
    )
    assert scent_weights(positive) == distribution
    distribution.clear()
    assert estimator.distribution()

    estimator.update(empty)
    uniform = estimator.distribution()
    assert len(set(uniform.values())) == 1
    assert sum(uniform.values()) == pytest.approx(1)
    assert _digest(_distribution_vector(uniform)) == (
        "4a00b8abf1902a917730683133aed588d4b976dcedeed30d6677a10ace584100"
    )


def test_trajectory_initial_multiple_updates_and_immutable_vectors() -> None:
    first, second = _observations()
    estimator = TrajectoryBeamBelief(history_k=3, beam_width=32)
    estimator.update(first)
    initial = estimator.diagnostics()
    initial_vector = [
        _distribution_vector(estimator.distribution()),
        _trajectory_vector(estimator.trajectories),
        [initial.updates, initial.hypotheses, initial.entropy],
    ]
    assert (
        _digest(initial_vector)
        == "2fe7e6590d5e2d9bfdefd564b01fd9d03ef502eba68329d623d785b62974c5be"
    )
    assert isinstance(estimator.trajectories, tuple)
    assert all(isinstance(path, tuple) for path in estimator.trajectories)

    estimator.update(second)
    multiple = estimator.diagnostics()
    multiple_vector = [
        _distribution_vector(estimator.distribution()),
        _trajectory_vector(estimator.trajectories),
        [multiple.updates, multiple.hypotheses, multiple.entropy],
    ]
    assert (
        _digest(multiple_vector)
        == "0cd0fc67b1b1b49c458da3779f9e5ebfa1ecd05a0ad959b44a53f09c2626463b"
    )
    assert sum(estimator.distribution().values()) == pytest.approx(1)
    copied = estimator.distribution()
    copied.clear()
    assert estimator.distribution()
    assert multiple.last_update_seconds >= 0


@pytest.mark.parametrize(("history_k", "beam_width"), [(0, 1), (1, 0), (-1, 2), (2, -1)])
def test_invalid_constructor_values_preserve_exception(history_k: int, beam_width: int) -> None:
    with pytest.raises(ValueError, match="^history_k and beam_width must be positive$"):
        TrajectoryBeamBelief(history_k, beam_width)


def test_belief_contract_has_no_hidden_truth_input_or_output() -> None:
    observation, _ = _observations()
    assert WorldState not in {type(observation), *(field.type for field in fields(Observation))}
    for estimator in (CurrentScentBelief(), TrajectoryBeamBelief(3, 32)):
        estimator.update(observation)
        assert not hasattr(estimator, "world_state")
        assert not hasattr(estimator, "true_position")
        assert all(isinstance(position, Position) for position in estimator.distribution())
