"""Typed controls and diagnostics for deterministic Phase 3B search."""

from dataclasses import dataclass
from enum import Enum

from ..models import Action, Position


class OpponentModel(str, Enum):
    """Legally reconstructible deterministic Thief response models."""

    SIMPLE_EVASION = "simple_evasion"
    SCENT_EVASION_MODEL = "scent_evasion_model"
    LOOKAHEAD_EVASION_MODEL = "lookahead_evasion_model"


class BeliefUsage(str, Enum):
    """Controlled ways of consuming an existing belief marginal."""

    HOTTEST_CELL = "hottest_cell"
    TOP3_WEIGHTED = "top3_weighted"
    FULL = "full"


FEATURES = (
    "distance_pursuit",
    "capture_probability",
    "reachable_area_reduction",
    "opponent_mobility",
    "police_mobility",
    "barrier_cost",
    "bottleneck_separator",
    "self_isolation_risk",
    "survival_horizon_urgency",
)


@dataclass(frozen=True, slots=True)
class ActionDiagnostic:
    """Truth-free explanation of a scored root action."""

    action: Action
    score: float
    components: dict[str, float]
    modeled_replies: tuple[Position, ...]
