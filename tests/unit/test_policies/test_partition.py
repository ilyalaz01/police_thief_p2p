"""Known-board separator planning tests."""

from police_thief_lab import Action, GameConfig, Position, Role, Simulator
from police_thief_lab.policies import SeparatorVariant, plan_separator


def _police_observation():
    simulator = Simulator(GameConfig())
    simulator.apply(Action.stay())
    return simulator.observe(Role.POLICE)


def test_closed_wall_plan_is_an_interior_complete_line() -> None:
    """Closed-wall planning returns a deterministic graph separator candidate."""
    observation = _police_observation()
    plan = plan_separator(observation, SeparatorVariant.CLOSED_WALL)
    assert plan.axis in {"horizontal", "vertical"}
    assert 0 < plan.index < observation.board_size - 1
    assert len(plan.targets) == observation.board_size
    assert plan.gap is None
    if plan.axis == "vertical":
        assert {cell.col for cell in plan.targets} == {plan.index}
    else:
        assert {cell.row for cell in plan.targets} == {plan.index}


def test_controlled_gap_removes_one_near_police_cell() -> None:
    """The funnel variant leaves exactly one explicit temporary public gate."""
    observation = _police_observation()
    plan = plan_separator(observation, SeparatorVariant.CONTROLLED_GAP)
    assert plan.gap is not None
    assert plan.gap not in plan.targets
    assert len(plan.targets) == observation.board_size - 1


def test_static_obstacle_contributes_to_separator() -> None:
    """A static obstacle on the selected line reduces required barrier cost."""
    config = GameConfig(blocked_cells=frozenset({Position(3, 1), Position(3, 2), Position(3, 4)}))
    simulator = Simulator(config)
    simulator.apply(Action.stay())
    plan = plan_separator(simulator.observe(Role.POLICE), SeparatorVariant.CLOSED_WALL)
    assert all(cell not in config.blocked_cells for cell in plan.targets)
    assert len(plan.targets) <= config.board_size
