"""Pure board geometry, action legality, terminal rules, and scoring."""

from __future__ import annotations

from .models import (
    Action,
    BarrierPlacementMode,
    Direction,
    GameConfig,
    MoveType,
    Position,
    Role,
    Score,
    TerminalReason,
    WorldState,
)

ORTHOGONAL = (Direction.N, Direction.S, Direction.E, Direction.W)
DELTAS = {
    Direction.N: (-1, 0),
    Direction.S: (1, 0),
    Direction.E: (0, 1),
    Direction.W: (0, -1),
    Direction.STAY: (0, 0),
}


class IllegalAction(ValueError):  # noqa: N818 - domain term used by the public API
    """Raised before any state mutation when an action violates game physics."""


def in_bounds(position: Position, config: GameConfig) -> bool:
    """Return whether a coordinate lies on the configured square board."""
    return 0 <= position.row < config.board_size and 0 <= position.col < config.board_size


def step(position: Position, direction: Direction) -> Position:
    """Apply one fixed direction without checking board constraints."""
    row_delta, col_delta = DELTAS[direction]
    return Position(position.row + row_delta, position.col + col_delta)


def blocked_positions(state: WorldState, config: GameConfig) -> frozenset[Position]:
    """Combine permanent terrain and persistent placed barriers."""
    return state.blocked_cells | frozenset(barrier.position for barrier in state.barriers)


def legal_move_directions(
    position: Position, state: WorldState, config: GameConfig
) -> tuple[Direction, ...]:
    """Return legal orthogonal directions plus STAY in stable deterministic order."""
    blocked = blocked_positions(state, config)
    moves = tuple(
        direction
        for direction in ORTHOGONAL
        if in_bounds(step(position, direction), config) and step(position, direction) not in blocked
    )
    return (*moves, Direction.STAY)


def barrier_targets(state: WorldState, config: GameConfig) -> tuple[Position, ...]:
    """Return Police targets under the explicitly negotiated placement mode."""
    if state.police_barriers_placed >= config.barrier_quota:
        return ()
    candidates = [step(state.police_position, direction) for direction in ORTHOGONAL]
    if config.barrier_placement_mode is BarrierPlacementMode.OWN_PLUS_ADJACENT:
        candidates.insert(0, state.police_position)
    blocked = blocked_positions(state, config)
    return tuple(
        position
        for position in candidates
        if in_bounds(position, config) and position not in blocked
    )


def legal_actions(role: Role, state: WorldState, config: GameConfig) -> tuple[Action, ...]:
    """List every legal action for a role in deterministic order."""
    if state.terminal_reason is not None or role is not state.next_role:
        return ()
    position = state.police_position if role is Role.POLICE else state.thief_position
    moves = tuple(
        Action.stay() if direction is Direction.STAY else Action.move(direction)
        for direction in legal_move_directions(position, state, config)
    )
    if role is Role.POLICE:
        return moves + tuple(Action.barrier(target) for target in barrier_targets(state, config))
    return moves


def validate_action(action: Action, role: Role, state: WorldState, config: GameConfig) -> None:
    """Reject malformed or illegal actions without forgiving them into STAY."""
    if action not in legal_actions(role, state, config):
        raise IllegalAction(f"illegal {role.value} action: {action}")
    if action.move_type is MoveType.MOVE and action.direction not in ORTHOGONAL:
        raise IllegalAction("MOVE requires one orthogonal direction")


def thief_boxed_in(state: WorldState, config: GameConfig) -> bool:
    """Implement Appendix-E Rule 47; STAY does not provide an escape."""
    blocked = blocked_positions(state, config)
    return all(
        not in_bounds(step(state.thief_position, direction), config)
        or step(state.thief_position, direction) in blocked
        for direction in ORTHOGONAL
    )


def score_for(reason: TerminalReason) -> Score:
    """Return the fixed Appendix-F sub-game score."""
    if reason is TerminalReason.THIEF_SURVIVED:
        return Score(police=5, thief=10)
    return Score(police=20, thief=5)
