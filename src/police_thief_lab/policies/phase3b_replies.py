"""Legally reconstructible Phase 3B reply and action enumeration helpers."""

from ..models import Action, Direction, Position
from .geometry import manhattan, neighbours, reachable_area
from .phase3b_models import OpponentModel


def modeled_replies(model, thief, police, size, obstacles, police_scent):
    """Return all top-ranked replies; randomness in frozen policies is represented as ties."""
    cells = (*neighbours(thief, size, obstacles), thief)
    if model is OpponentModel.SIMPLE_EVASION:
        scores = {
            cell: (manhattan(cell, police), len(neighbours(cell, size, obstacles)))
            for cell in cells
        }
    elif model is OpponentModel.SCENT_EVASION_MODEL:
        scent = dict(police_scent)
        scores = {
            cell: (
                -scent.get(cell, 0.0),
                reachable_area(cell, size, obstacles),
                len(neighbours(cell, size, obstacles)),
                min(cell.row, cell.col, size - 1 - cell.row, size - 1 - cell.col),
            )
            for cell in cells
        }
    else:
        scent = dict(police_scent)
        scores = {}
        for cell in cells:
            future = []
            for next_cell in (*neighbours(cell, size, obstacles), cell):
                exits = neighbours(next_cell, size, obstacles)
                independent = len(
                    {
                        candidate
                        for exit_cell in exits
                        for candidate in neighbours(exit_cell, size, obstacles)
                    }
                )
                future.append(
                    (
                        -scent.get(next_cell, 0.0),
                        reachable_area(next_cell, size, obstacles),
                        len(exits),
                        independent,
                        -int(len(exits) <= 1),
                    )
                )
            scores[cell] = min(future)
    best = max(scores.values())
    return tuple(cell for cell in cells if scores[cell] == best)


def _hypothetical_police_actions(position, size, obstacles, placed, quota):
    """Compute the internal hypothetical police actions step used by module."""
    directions = (Direction.N, Direction.S, Direction.E, Direction.W)
    moves = tuple(
        Action.move(direction)
        for direction, cell in zip(
            directions,
            (
                Position(position.row - 1, position.col),
                Position(position.row + 1, position.col),
                Position(position.row, position.col + 1),
                Position(position.row, position.col - 1),
            ),
            strict=True,
        )
        if cell in neighbours(position, size, obstacles)
    )
    barriers = (
        tuple(Action.barrier(cell) for cell in neighbours(position, size, obstacles))
        if placed < quota
        else ()
    )
    return (*moves, Action.stay(), *barriers)
