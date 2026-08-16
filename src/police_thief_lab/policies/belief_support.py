"""Private pure calculations shared by belief estimators."""

import math

from ..models import Observation, Position
from .geometry import blocked


def _open_cells(observation: Observation) -> tuple[Position, ...]:
    obstacles = blocked(observation)
    return tuple(
        Position(row, col)
        for row in range(observation.board_size)
        for col in range(observation.board_size)
        if Position(row, col) not in obstacles
    )


def _field_error(
    predicted: dict[Position, float], observed: dict[Position, float], size: int
) -> float:
    return sum(
        abs(predicted.get(Position(row, col), 0.0) - observed.get(Position(row, col), 0.0))
        for row in range(size)
        for col in range(size)
    ) / (size * size)


def _entropy(distribution: dict[Position, float]) -> float:
    return -sum(
        probability * math.log(probability)
        for probability in distribution.values()
        if probability > 0
    )
