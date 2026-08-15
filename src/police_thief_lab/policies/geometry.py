"""Small public-board graph helpers shared by explainable baselines."""

from __future__ import annotations

from collections import deque

from ..models import Action, MoveType, Observation, Position


def target_of(action: Action, origin: Position) -> Position:
    """Return the public destination of a legal move or STAY action."""
    if action.move_type is not MoveType.MOVE:
        return origin
    deltas = {"N": (-1, 0), "S": (1, 0), "E": (0, 1), "W": (0, -1)}
    row, col = deltas[action.direction.value]
    return Position(origin.row + row, origin.col + col)


def blocked(observation: Observation) -> frozenset[Position]:
    """Return all publicly impassable cells without conflating their semantics."""
    return observation.blocked_cells | frozenset(b.position for b in observation.barriers)


def neighbours(
    position: Position, size: int, obstacles: frozenset[Position]
) -> tuple[Position, ...]:
    """Return unblocked orthogonal neighbours in deterministic order."""
    candidates = (
        Position(position.row - 1, position.col),
        Position(position.row + 1, position.col),
        Position(position.row, position.col + 1),
        Position(position.row, position.col - 1),
    )
    return tuple(
        cell
        for cell in candidates
        if 0 <= cell.row < size and 0 <= cell.col < size and cell not in obstacles
    )


def reachable_area(start: Position, size: int, obstacles: frozenset[Position]) -> int:
    """Count the public-board component reachable from a candidate cell."""
    if start in obstacles:
        return 0
    seen = {start}
    queue = deque([start])
    while queue:
        for cell in neighbours(queue.popleft(), size, obstacles):
            if cell not in seen:
                seen.add(cell)
                queue.append(cell)
    return len(seen)


def manhattan(left: Position, right: Position) -> int:
    """Return orthogonal grid distance."""
    return abs(left.row - right.row) + abs(left.col - right.col)
