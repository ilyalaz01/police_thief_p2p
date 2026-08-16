"""Public Phase 1 SDK surface for the Police-Thief game laboratory."""

from .models import (
    Action,
    Barrier,
    BarrierPlacementMode,
    Direction,
    GameConfig,
    MoveType,
    Observation,
    Position,
    Role,
    RoleLocalState,
    Score,
    TerminalReason,
    TurnModel,
    WorldState,
)
from .rules import IllegalAction
from .scent import ReferenceSubtractiveChebyshevV1, ScentModel
from .sdk import PeerLaunchRequest, PoliceThiefSDK
from .simulator import DecisionBackend, Simulator, replay

__version__ = "1.0.0"
__all__ = [
    "Action",
    "Barrier",
    "BarrierPlacementMode",
    "DecisionBackend",
    "Direction",
    "GameConfig",
    "IllegalAction",
    "MoveType",
    "Observation",
    "PeerLaunchRequest",
    "PoliceThiefSDK",
    "Position",
    "ReferenceSubtractiveChebyshevV1",
    "Role",
    "RoleLocalState",
    "ScentModel",
    "Score",
    "Simulator",
    "TerminalReason",
    "TurnModel",
    "WorldState",
    "replay",
]
