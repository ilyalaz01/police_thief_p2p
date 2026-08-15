"""Phase 3B repaired-search behavior and isolation tests."""

from police_thief_lab import Action, Direction, GameConfig, Role, Simulator
from police_thief_lab.policies import (
    BeliefUsage,
    DeterministicSearchPolice,
    OpponentModel,
    TacticalOneStepPolice,
)


def _first_police_observation():
    simulator = Simulator(GameConfig())
    simulator.apply(Action.move(Direction.N))
    return simulator.observe(Role.POLICE)


def test_phase3b_search_is_legal_deterministic_and_explained() -> None:
    observation = _first_police_observation()
    left = DeterministicSearchPolice(17, node_budget=64)
    right = DeterministicSearchPolice(17, node_budget=64)
    assert left.choose_action(observation) == right.choose_action(observation)
    assert left.last_diagnostics
    assert {row.action for row in left.last_diagnostics} == set(observation.legal_actions)
    assert all(row.components for row in left.last_diagnostics)


def test_phase3b_control_enums_are_exhaustive() -> None:
    assert len(OpponentModel) == 3
    assert len(BeliefUsage) == 3


def test_tactical_one_step_is_legal() -> None:
    observation = _first_police_observation()
    assert TacticalOneStepPolice(4).choose_action(observation) in observation.legal_actions


def test_normal_search_has_no_oracle_switch() -> None:
    policy = DeterministicSearchPolice(1)
    assert not hasattr(policy, "oracle")
    assert not hasattr(policy, "true_position")
    assert not hasattr(policy, "actual_reply")
