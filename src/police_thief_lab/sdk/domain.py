"""Domain and deterministic simulation operations exposed through the SDK."""

from ..models import (
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
    StartValidationProfile,
    TerminalReason,
    TurnModel,
    WorldState,
)
from ..rules import (
    IllegalAction,
    barrier_targets,
    blocked_positions,
    in_bounds,
    legal_actions,
    legal_move_directions,
    score_for,
    step,
    thief_boxed_in,
    validate_action,
)
from ..scent import ReferenceSubtractiveChebyshevV1, ScentModel, scent_model_for
from ..simulator import DecisionBackend, Simulator, replay
from ..turns import ReferenceV3Alternating


class DomainSDK:
    """Stable access to domain types, rules, scent, turns, simulation, and replay."""

    Action = Action
    Barrier = Barrier
    BarrierPlacementMode = BarrierPlacementMode
    DecisionBackend = DecisionBackend
    Direction = Direction
    GameConfig = GameConfig
    IllegalAction = IllegalAction
    MoveType = MoveType
    Observation = Observation
    Position = Position
    ReferenceSubtractiveChebyshevV1 = ReferenceSubtractiveChebyshevV1
    ReferenceV3Alternating = ReferenceV3Alternating
    Role = Role
    RoleLocalState = RoleLocalState
    Score = Score
    ScentModel = ScentModel
    Simulator = Simulator
    StartValidationProfile = StartValidationProfile
    TerminalReason = TerminalReason
    TurnModel = TurnModel
    WorldState = WorldState
    barrier_targets = staticmethod(barrier_targets)
    blocked_positions = staticmethod(blocked_positions)
    in_bounds = staticmethod(in_bounds)
    legal_actions = staticmethod(legal_actions)
    legal_move_directions = staticmethod(legal_move_directions)
    replay = staticmethod(replay)
    scent_model_for = staticmethod(scent_model_for)
    score_for = staticmethod(score_for)
    step = staticmethod(step)
    thief_boxed_in = staticmethod(thief_boxed_in)
    validate_action = staticmethod(validate_action)
