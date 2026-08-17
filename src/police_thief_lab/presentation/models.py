"""Immutable, nonce-free view models for live and replay presentation."""

from __future__ import annotations

import math
from dataclasses import asdict, dataclass
from enum import Enum
from typing import Any

from ..models import Observation, Position


class TurnBanner(str, Enum):
    """Official live-view input states."""

    YOUR_TURN = "YOUR TURN"
    LOCKED = "LOCKED"
    GAME_OVER = "GAME OVER"
    ERROR = "ERROR"


@dataclass(frozen=True, slots=True)
class RoleLocalView:
    """One peer's legal live view; hidden opponent truth has no field."""

    board_size: int
    role: str
    own_position: tuple[int, int]
    blocked_cells: tuple[tuple[int, int], ...]
    barriers: tuple[tuple[int, int], ...]
    belief: tuple[tuple[int, int, float], ...]
    banner: str
    step: int

    def to_object(self) -> dict[str, Any]:
        """Return JSON-ready local truth without introducing opponent position."""
        return asdict(self)


@dataclass(frozen=True, slots=True)
class ReplayFrame:
    """Post-game truth at one verified replay point."""

    index: int
    step: int
    police_position: tuple[int, int]
    thief_position: tuple[int, int]
    blocked_cells: tuple[tuple[int, int], ...]
    barriers: tuple[tuple[int, int], ...]
    actor: str | None


@dataclass(frozen=True, slots=True)
class ReplayView:
    """Sanitized replay model that deliberately excludes records and nonces."""

    game_id: str
    board_size: int
    result: str
    frames: tuple[ReplayFrame, ...]
    verdict: str
    failed_commit_indices: tuple[int, ...]
    physics_errors: tuple[str, ...]

    def to_object(self) -> dict[str, Any]:
        """Return only fields required by the standalone viewer."""
        return asdict(self)


def _cell(position: Position) -> tuple[int, int]:
    """Compute the internal cell step used by module."""
    return position.row, position.col


def build_live_view(
    observation: Observation,
    belief: dict[Position, float],
    banner: TurnBanner,
    step: int,
) -> RoleLocalView:
    """Project a legal policy observation and truth-free belief into a view."""
    if step < 0:
        raise ValueError("step must be non-negative")
    for cell, probability in belief.items():
        if not 0 <= cell.row < observation.board_size or not 0 <= cell.col < observation.board_size:
            raise ValueError("belief cell must be on the board")
        if not math.isfinite(probability) or probability < 0:
            raise ValueError("belief probability must be finite and non-negative")
    return RoleLocalView(
        board_size=observation.board_size,
        role=observation.local.role.value,
        own_position=_cell(observation.local.own_position),
        blocked_cells=tuple(sorted(_cell(cell) for cell in observation.blocked_cells)),
        barriers=tuple(sorted(_cell(item.position) for item in observation.barriers)),
        belief=tuple(sorted((cell.row, cell.col, value) for cell, value in belief.items())),
        banner=banner.value,
        step=step,
    )
