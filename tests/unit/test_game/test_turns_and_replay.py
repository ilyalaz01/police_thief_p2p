"""Alternating cadence, terminal timing, and deterministic replay tests."""

import pytest

from police_thief_lab import (
    Action,
    Direction,
    GameConfig,
    IllegalAction,
    Position,
    Role,
    Score,
    Simulator,
    TerminalReason,
    replay,
)


def test_thief_acts_first_and_turns_alternate() -> None:
    """REFERENCE_V3_ALTERNATING passes one serial turn token, starting at Thief."""
    simulator = Simulator(GameConfig())
    assert simulator.state.next_role is Role.THIEF
    simulator.apply(Action.move(Direction.E))
    assert simulator.state.next_role is Role.POLICE
    simulator.apply(Action.move(Direction.S))
    assert simulator.state.next_role is Role.THIEF


def test_wrong_role_has_no_legal_actions() -> None:
    """Only the token owner can act through the strategy-facing observation."""
    simulator = Simulator(GameConfig())
    assert simulator.observe(Role.POLICE).legal_actions == ()
    assert simulator.observe(Role.THIEF).legal_actions


def test_police_post_action_claim_captures() -> None:
    """A Police move onto the Thief settles on that Police action."""
    config = GameConfig(police_start=Position(3, 1), thief_start=Position(3, 3))
    simulator = Simulator(config)
    simulator.apply(Action.move(Direction.W))
    state = simulator.apply(Action.move(Direction.E))
    assert state.terminal_reason is TerminalReason.POLICE_CAPTURE
    assert state.score == Score(20, 5)


def test_thief_entering_police_cell_waits_for_police_claim() -> None:
    """Reference cadence has no automatic shared-state collision on a Thief action."""
    config = GameConfig(police_start=Position(3, 2), thief_start=Position(3, 3))
    simulator = Simulator(config)
    state = simulator.apply(Action.move(Direction.W))
    assert state.terminal_reason is None
    state = simulator.apply(Action.stay())
    assert state.terminal_reason is TerminalReason.POLICE_CAPTURE


def test_survival_exactly_at_threshold() -> None:
    """The 35th Thief action wins immediately; Police has acted only 34 times."""
    simulator = Simulator(GameConfig())
    for turn in range(69):
        state = simulator.apply(Action.stay())
        if turn < 68:
            assert state.terminal_reason is None
    assert state.terminal_reason is TerminalReason.THIEF_SURVIVED
    assert (state.thief_moves, state.police_moves) == (35, 34)
    assert state.score == Score(5, 10)
    with pytest.raises(IllegalAction):
        simulator.apply(Action.stay())


def test_action_sequence_and_replay_are_identical() -> None:
    """Two executions of the same serial actions reproduce complete truth exactly."""
    actions = (
        Action.move(Direction.E),
        Action.move(Direction.S),
        Action.stay(),
        Action.barrier(Position(1, 1)),
        Action.move(Direction.S),
    )
    config = GameConfig()
    simulator = Simulator(config)
    states = [simulator.apply(action) for action in actions]
    assert simulator.action_log == actions
    assert replay(config, actions) == states[-1]
    assert replay(config, actions) == replay(config, actions)
