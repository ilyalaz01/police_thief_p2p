"""Legality, determinism, and information-boundary tests for Phase 2 policies."""

from dataclasses import fields

import pytest

from police_thief_lab import Action, GameConfig, Observation, Role, Simulator
from police_thief_lab.policies import (
    PartitionPolice,
    RandomLegalPolice,
    RandomLegalThief,
    ScentGreedyPolice,
    SeparatorVariant,
    SpaceSeekingThief,
)


@pytest.mark.parametrize(
    ("factory", "role"),
    [
        (RandomLegalPolice, Role.POLICE),
        (RandomLegalThief, Role.THIEF),
        (ScentGreedyPolice, Role.POLICE),
        (SpaceSeekingThief, Role.THIEF),
        (PartitionPolice, Role.POLICE),
    ],
)
def test_every_baseline_returns_observed_legal_actions(factory: type, role: Role) -> None:
    """Policies choose strictly from the immutable legal-action tuple."""
    simulator = Simulator(GameConfig())
    if role is Role.POLICE:
        simulator.apply(Action.stay())
    observation = simulator.observe(role)
    action = factory(7).choose_action(observation)
    assert action in observation.legal_actions


def test_random_policy_seed_reproducibility() -> None:
    """Equal seeds and observations yield equal random action streams."""
    simulator = Simulator(GameConfig())
    observation = simulator.observe(Role.THIEF)
    left, right = RandomLegalThief(11), RandomLegalThief(11)
    assert [left.choose_action(observation) for _ in range(10)] == [
        right.choose_action(observation) for _ in range(10)
    ]


def test_policy_boundary_contains_no_hidden_truth_or_evaluator_diagnostics() -> None:
    """Neither opponent coordinates nor ground-truth separator diagnostics reach policies."""
    names = {field.name for field in fields(Observation)}
    forbidden = {
        "opponent_position",
        "thief_position",
        "world_state",
        "wrong_side_cuts",
        "unfinished_crossings",
        "actual_thief_side",
    }
    assert names.isdisjoint(forbidden)


@pytest.mark.parametrize("variant", list(SeparatorVariant))
def test_partition_policy_uses_observation_only(variant: SeparatorVariant) -> None:
    """Partition Police can plan and act from its Police observation alone."""
    simulator = Simulator(GameConfig())
    simulator.apply(Action.stay())
    policy = PartitionPolice(3, variant)
    action = policy.choose_action(simulator.observe(Role.POLICE))
    assert action in simulator.observe(Role.POLICE).legal_actions
    assert policy.plan is not None
