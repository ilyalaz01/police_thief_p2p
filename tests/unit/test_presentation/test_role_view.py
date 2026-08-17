"""Role-safe presentation-model contract tests."""

from dataclasses import replace

from police_thief_lab import Barrier, Position, Role, Simulator
from police_thief_lab.models import GameConfig
from police_thief_lab.presentation import TurnBanner, build_live_view


def test_live_view_contains_only_role_local_truth_and_belief() -> None:
    simulator = Simulator(GameConfig())
    observation = simulator.observe(Role.THIEF)

    view = build_live_view(
        observation,
        {Position(0, 0): 0.75, Position(0, 1): 0.25},
        TurnBanner.YOUR_TURN,
        step=0,
    )

    assert view.role == "thief"
    assert view.own_position == (3, 3)
    assert view.belief == ((0, 0, 0.75), (0, 1, 0.25))
    assert "opponent_position" not in view.to_object()
    assert view.banner == "YOUR TURN"


def test_live_view_sorts_public_barriers_and_rejects_bad_belief_cells() -> None:
    simulator = Simulator(GameConfig())
    observation = replace(
        simulator.observe(Role.THIEF),
        barriers=frozenset({Barrier(Position(2, 1)), Barrier(Position(1, 2))}),
    )

    view = build_live_view(observation, {}, TurnBanner.LOCKED, step=2)

    assert view.barriers == ((1, 2), (2, 1))
    assert view.banner == "LOCKED"
