"""Immutable domain types for the deterministic game laboratory."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class Role(str, Enum):
    """A player's role."""

    POLICE = "police"
    THIEF = "thief"


class Direction(str, Enum):
    """The fixed Appendix-F movement directions, including staying put."""

    N = "N"
    S = "S"
    E = "E"
    W = "W"
    STAY = "STAY"


class MoveType(str, Enum):
    """The mutually exclusive action kinds."""

    MOVE = "move"
    STAY = "stay"
    BARRIER = "barrier"


class BarrierPlacementMode(str, Enum):
    """The negotiated own-cell barrier dialect from the baseline."""

    ADJACENT_ONLY = "adjacent_only"
    OWN_PLUS_ADJACENT = "own_plus_adjacent"


class TurnModel(str, Enum):
    """Supported turn cadence; Phase 1 deliberately contains only reference v3."""

    REFERENCE_V3_ALTERNATING = "reference_v3_alternating"


class StartValidationProfile(str, Enum):
    """Negotiated validation policy; start separation is not an official invariant."""

    INTEROP = "interop"
    LAB_DISTINCT = "lab_distinct"


class TerminalReason(str, Enum):
    """A deterministic physical reason for a completed sub-game."""

    POLICE_CAPTURE = "police_capture"
    BARRIER_ON_THIEF = "barrier_on_thief"
    THIEF_BOXED_IN = "thief_boxed_in"
    THIEF_SURVIVED = "thief_survived"


@dataclass(frozen=True, slots=True, order=True)
class Position:
    """A zero-based board coordinate (row, column)."""

    row: int
    col: int


@dataclass(frozen=True, slots=True)
class Action:
    """A move, stay, or Police barrier placement."""

    move_type: MoveType
    direction: Direction | None = None
    barrier_position: Position | None = None

    @classmethod
    def move(cls, direction: Direction) -> Action:
        """Create a movement action; STAY has its own action kind."""
        return cls(MoveType.MOVE, direction=direction)

    @classmethod
    def stay(cls) -> Action:
        """Create the fifth legal movement action."""
        return cls(MoveType.STAY, direction=Direction.STAY)

    @classmethod
    def barrier(cls, position: Position) -> Action:
        """Create a barrier action targeted at an explicit public cell."""
        return cls(MoveType.BARRIER, barrier_position=position)


@dataclass(frozen=True, slots=True)
class Barrier:
    """A permanent public barrier and the role that placed it."""

    position: Position
    placed_by: Role = Role.POLICE


@dataclass(frozen=True, slots=True)
class Score:
    """Fixed Appendix-F points for one sub-game."""

    police: int
    thief: int


ScentField = tuple[tuple[Position, float], ...]


@dataclass(frozen=True, slots=True)
class GameConfig:
    """Shared, validated game parameters, including every negotiated Phase 1 rule."""

    board_size: int = 7
    police_start: Position = Position(0, 0)
    thief_start: Position = Position(3, 3)
    blocked_cells: frozenset[Position] = frozenset()
    barrier_quota: int = 14
    survival_threshold: int = 35
    barrier_placement_mode: BarrierPlacementMode = BarrierPlacementMode.ADJACENT_ONLY
    scent_profile: str = "subtractive_chebyshev_v1"
    turn_model: TurnModel = TurnModel.REFERENCE_V3_ALTERNATING
    start_validation_profile: StartValidationProfile = StartValidationProfile.INTEROP

    def __post_init__(self) -> None:
        """Enforce Appendix-F minima and coherent initial geometry."""
        if self.board_size < 7:
            raise ValueError("board_size must meet the Appendix F minimum of 7")
        if self.barrier_quota < 14:
            raise ValueError("barrier_quota must meet the Appendix F minimum of 14")
        if self.survival_threshold < 35:
            raise ValueError("survival_threshold must meet the Appendix F minimum of 35")
        occupied = self.blocked_cells | {self.police_start, self.thief_start}
        if any(
            not (0 <= p.row < self.board_size and 0 <= p.col < self.board_size) for p in occupied
        ):
            raise ValueError("starts and blocked cells must be in bounds")
        if self.police_start in self.blocked_cells or self.thief_start in self.blocked_cells:
            raise ValueError("a player cannot start on a blocked cell")
        if (
            self.start_validation_profile is StartValidationProfile.LAB_DISTINCT
            and self.police_start == self.thief_start
        ):
            raise ValueError("lab_distinct profile requires distinct starting cells")


@dataclass(frozen=True, slots=True)
class WorldState:
    """Complete simulator truth. This type never crosses the policy boundary."""

    police_position: Position
    thief_position: Position
    blocked_cells: frozenset[Position]
    barriers: frozenset[Barrier]
    next_role: Role
    police_moves: int = 0
    thief_moves: int = 0
    police_barriers_placed: int = 0
    police_scent: ScentField = ()
    thief_scent: ScentField = ()
    terminal_reason: TerminalReason | None = None
    score: Score | None = None


@dataclass(frozen=True, slots=True)
class RoleLocalState:
    """Truth legally local to one role."""

    role: Role
    own_position: Position
    own_moves: int
    own_barriers_placed: int


@dataclass(frozen=True, slots=True)
class Observation:
    """The only object a strategy receives; it contains no opponent coordinate."""

    local: RoleLocalState
    board_size: int
    barrier_quota: int
    blocked_cells: frozenset[Position]
    barriers: frozenset[Barrier]
    opponent_scent: ScentField
    legal_actions: tuple[Action, ...]
    terminal_reason: TerminalReason | None
