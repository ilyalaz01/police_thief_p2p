"""Leakage, ablation, and stronger-baseline validation tests."""

from dataclasses import fields, is_dataclass

import pytest

from police_thief_lab import Action, GameConfig, Observation, Role, Simulator, WorldState
from police_thief_lab.evaluation import AblatedBackend, ScentAblation
from police_thief_lab.policies import (
    BarrierAwareThief,
    ScentEvasionThief,
    ScentGreedyPolice,
    ScentTacticalPolice,
)


def _walk_types(value, seen=None):
    seen = seen or set()
    if id(value) in seen:
        return []
    seen.add(id(value))
    found = [type(value)]
    if is_dataclass(value):
        for field in fields(value):
            found.extend(_walk_types(getattr(value, field.name), seen))
    elif isinstance(value, tuple | frozenset | list | dict):
        items = value.items() if isinstance(value, dict) else value
        for item in items:
            found.extend(_walk_types(item, seen))
    return found


def test_scent_greedy_recursive_input_graph_excludes_hidden_truth() -> None:
    """No direct or nested value reachable from the observation is WorldState/evaluator truth."""
    simulator = Simulator(GameConfig())
    simulator.apply(Action.stay())
    observation = simulator.observe(Role.POLICE)
    assert WorldState not in _walk_types(observation)
    forbidden = {
        "thief_position",
        "opponent_position",
        "actual_hidden_side",
        "wrong_side_cuts",
        "future_actions",
        "simulator",
        "evaluator",
    }
    assert {field.name for field in fields(Observation)}.isdisjoint(forbidden)
    assert not hasattr(observation, "callback")


def test_scent_greedy_policy_holds_only_rng_not_callbacks_or_evaluator() -> None:
    """Policy private state contains seeded RNG only, with no simulator/callback reference."""
    policy = ScentGreedyPolice(4)
    assert set(vars(policy)) == {"_random"}
    assert not callable(policy._random)


@pytest.mark.parametrize("mode", list(ScentAblation))
def test_ablation_changes_only_scent_and_returns_legal_action(mode: ScentAblation) -> None:
    """Evaluation ablations preserve every non-scent observation field and action legality."""
    simulator = Simulator(GameConfig())
    simulator.apply(Action.stay())
    observation = simulator.observe(Role.POLICE)
    wrapper = AblatedBackend(ScentGreedyPolice(1), mode, 1)
    assert wrapper.choose_action(observation) in observation.legal_actions


@pytest.mark.parametrize("policy_type", [ScentEvasionThief, BarrierAwareThief])
def test_stronger_thieves_always_choose_legal_observed_action(policy_type: type) -> None:
    """New adversaries use only their legal Thief observation."""
    simulator = Simulator(GameConfig())
    observation = simulator.observe(Role.THIEF)
    assert policy_type(9).choose_action(observation) in observation.legal_actions


def test_tactical_police_returns_legal_action_and_tracks_attempts() -> None:
    """Sparse tactical logic remains inside the observation boundary."""
    simulator = Simulator(GameConfig())
    simulator.apply(Action.stay())
    observation = simulator.observe(Role.POLICE)
    policy = ScentTacticalPolice(2)
    assert policy.choose_action(observation) in observation.legal_actions
    assert not hasattr(policy, "simulator")
