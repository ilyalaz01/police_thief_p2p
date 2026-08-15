"""Movement, barrier, Rule 46/47, counters, and scoring tests."""

import pytest

from police_thief_lab import (
    Action,
    BarrierPlacementMode,
    Direction,
    GameConfig,
    IllegalAction,
    Position,
    Role,
    Score,
    Simulator,
    TerminalReason,
)


@pytest.mark.parametrize(
    ("direction", "expected"),
    [
        (Direction.N, Position(2, 3)),
        (Direction.S, Position(4, 3)),
        (Direction.E, Position(3, 4)),
        (Direction.W, Position(3, 2)),
    ],
)
def test_all_orthogonal_directions(direction: Direction, expected: Position) -> None:
    """Every mandatory direction moves exactly one cell and increments only Thief."""
    simulator = Simulator(GameConfig())
    state = simulator.apply(Action.move(direction))
    assert state.thief_position == expected
    assert (state.thief_moves, state.police_moves) == (1, 0)


def test_stay_is_legal_and_counts() -> None:
    """STAY preserves position, emits scent, and counts as a Thief move."""
    simulator = Simulator(GameConfig())
    state = simulator.apply(Action.stay())
    assert state.thief_position == Position(3, 3)
    assert state.thief_moves == 1
    assert dict(state.thief_scent)[Position(3, 3)] == 0.8


@pytest.mark.parametrize("direction", [Direction.N, Direction.W])
def test_corner_boundaries_reject_without_mutation(direction: Direction) -> None:
    """Off-board movement is illegal and leaves complete state unchanged."""
    config = GameConfig(police_start=Position(6, 6), thief_start=Position(0, 0))
    simulator = Simulator(config)
    before = simulator.state
    with pytest.raises(IllegalAction):
        simulator.apply(Action.move(direction))
    assert simulator.state == before


def test_blocked_cell_and_diagonal_are_illegal() -> None:
    """Permanent terrain blocks movement and diagonal values cannot enter the domain."""
    simulator = Simulator(GameConfig(blocked_cells=frozenset({Position(2, 3)})))
    with pytest.raises(IllegalAction):
        simulator.apply(Action.move(Direction.N))
    with pytest.raises(ValueError):
        Direction("NE")


def test_static_terrain_is_not_a_police_barrier_or_quota_usage() -> None:
    """Static blocked cells stay visible and semantically separate from placed barriers."""
    terrain = frozenset({Position(2, 3)})
    simulator = Simulator(GameConfig(blocked_cells=terrain))
    state = simulator.state
    observation = simulator.observe(Role.THIEF)
    assert state.blocked_cells == terrain
    assert observation.blocked_cells == terrain
    assert state.barriers == frozenset()
    assert observation.barriers == frozenset()
    assert state.police_barriers_placed == 0

    simulator.apply(Action.stay())
    police_observation = simulator.observe(Role.POLICE)
    assert police_observation.local.own_barriers_placed == 0


def _advance_to_police(simulator: Simulator) -> None:
    simulator.apply(Action.stay())


def test_adjacent_only_barriers_persist_and_existing_target_is_rejected() -> None:
    """A Police barrier consumes its turn, persists, and cannot be placed twice."""
    simulator = Simulator(GameConfig())
    _advance_to_police(simulator)
    target = Position(0, 1)
    state = simulator.apply(Action.barrier(target))
    assert target in {barrier.position for barrier in state.barriers}
    assert state.police_position == Position(0, 0)
    assert (state.police_moves, state.police_barriers_placed) == (1, 1)
    simulator.apply(Action.stay())
    with pytest.raises(IllegalAction):
        simulator.apply(Action.barrier(target))


def test_placed_barrier_blocks_later_thief_movement() -> None:
    """A public barrier remains impassable to the Thief on later turns."""
    config = GameConfig(police_start=Position(2, 2), thief_start=Position(3, 3))
    simulator = Simulator(config)
    simulator.apply(Action.stay())
    simulator.apply(Action.barrier(Position(2, 3)))
    with pytest.raises(IllegalAction):
        simulator.apply(Action.move(Direction.N))


def test_barrier_placement_modes() -> None:
    """Own-cell placement is controlled only by the negotiated config field."""
    own = Position(0, 0)
    adjacent = Simulator(GameConfig())
    _advance_to_police(adjacent)
    assert Action.barrier(own) not in adjacent.observe(Role.POLICE).legal_actions
    with pytest.raises(IllegalAction):
        adjacent.apply(Action.barrier(own))

    own_plus = Simulator(GameConfig(barrier_placement_mode=BarrierPlacementMode.OWN_PLUS_ADJACENT))
    _advance_to_police(own_plus)
    assert Action.barrier(own) in own_plus.observe(Role.POLICE).legal_actions


def test_rule_46_barrier_on_thief_is_immediate_capture() -> None:
    """Appendix-E Rule 46 settles before the Thief gets another action."""
    config = GameConfig(thief_start=Position(0, 1))
    simulator = Simulator(config)
    _advance_to_police(simulator)
    state = simulator.apply(Action.barrier(Position(0, 1)))
    assert state.terminal_reason is TerminalReason.BARRIER_ON_THIEF
    assert state.score == Score(20, 5)


def test_rule_47_corner_box_in_is_capture() -> None:
    """At a corner two persistent barriers remove every orthogonal escape."""
    config = GameConfig(police_start=Position(1, 1), thief_start=Position(0, 0))
    simulator = Simulator(config)
    simulator.apply(Action.stay())
    simulator.apply(Action.barrier(Position(0, 1)))
    simulator.apply(Action.stay())
    state = simulator.apply(Action.barrier(Position(1, 0)))
    assert state.terminal_reason is TerminalReason.THIEF_BOXED_IN
    assert state.score == Score(20, 5)
