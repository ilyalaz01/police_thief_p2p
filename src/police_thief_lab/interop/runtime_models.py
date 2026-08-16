"""State and conversion helpers shared by the peer runtime modules."""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from ..models import (
    Action,
    BarrierPlacementMode,
    GameConfig,
    Position,
    Role,
)
from .profile import MatchProfile


class PeerPhase(str, Enum):
    STARTING = "starting"
    NEGOTIATING = "negotiating"
    WAITING = "waiting"
    ACTING = "acting"
    AUDITING = "auditing"
    VERIFIED = "verified"
    FAILED = "failed"


UNRESOLVED_GIT_COMMIT = "UNRESOLVED_SELF_TEST_NO_GIT_METADATA"


def require_real_team_git_commit(value: Any, owner: str) -> None:
    """Reject only values forbidden by the explicit real-team provenance gate."""
    if value is None or value == "" or value == UNRESOLVED_GIT_COMMIT:
        raise ValueError(f"real-team Git provenance refused: {owner} commit is unresolved")


@dataclass(slots=True)
class DeadlineTracker:
    timeout: float
    started: float = field(default_factory=time.monotonic)

    def remaining(self) -> float:
        return max(0.0, self.timeout - (time.monotonic() - self.started))


@dataclass(slots=True)
class LocalGameState:
    role: Role
    position: Position
    blocked: frozenset[Position]
    barriers: set[Position] = field(default_factory=set)
    own_moves: int = 0
    own_barriers: int = 0
    own_scent: tuple = ()
    opponent_scent: tuple = ()
    terminal: str | None = None
    pending_claim_response: dict[str, Any] | None = None


def _position(raw: Any) -> Position:
    return Position(int(raw[0]), int(raw[1]))


def config_from_profile(profile: MatchProfile) -> GameConfig:
    cfg = profile.board_config
    return GameConfig(
        board_size=cfg["board_size"],
        police_start=_position(cfg["police_start"]),
        thief_start=_position(cfg["thief_start"]),
        blocked_cells=frozenset(_position(p) for p in cfg.get("blocked_cells", [])),
        barrier_quota=cfg.get("barrier_quota", 14),
        survival_threshold=profile.survival_limit,
        barrier_placement_mode=BarrierPlacementMode(profile.barrier_placement_profile.lower()),
        scent_profile=profile.scent_profile,
    )


def action_to_wire(action: Action | None) -> dict[str, Any] | None:
    if action is None:
        return None
    return {
        "type": action.move_type.value,
        "direction": action.direction.value if action.direction else None,
        "barrier": (
            [action.barrier_position.row, action.barrier_position.col]
            if action.barrier_position
            else None
        ),
    }


def _audit_result(value: str | None) -> str | None:
    if value in {"police_capture", "barrier_on_thief", "thief_boxed_in"}:
        return "capture"
    return value
