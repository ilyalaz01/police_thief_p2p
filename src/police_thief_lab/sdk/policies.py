"""Policy constructors and diagnostics exposed through the SDK."""

from ..policies import (
    AggregationMode,
    BarrierAwareThief,
    BeliefEstimator,
    BeliefSearchPolice,
    BeliefUsage,
    CurrentScentBelief,
    DeterministicSearchPolice,
    LookaheadEvasionThief,
    OpponentModel,
    PartitionPolice,
    RandomLegalPolice,
    RandomLegalThief,
    ScentEvasionThief,
    ScentGreedyPolice,
    ScentTacticalPolice,
    SeparatorPlan,
    SeparatorVariant,
    SpaceSeekingThief,
    TacticalOneStepPolice,
    TrajectoryBeamBelief,
    plan_separator,
)
from ..policies.belief import scent_weights
from ..policies.geometry import blocked, manhattan, neighbours, reachable_area, target_of
from ..policies.phase3b import FEATURES, modeled_replies


class PoliciesSDK:
    """Stable policy catalogue and observation-only diagnostic operations."""

    AggregationMode = AggregationMode
    BarrierAwareThief = BarrierAwareThief
    BeliefEstimator = BeliefEstimator
    BeliefSearchPolice = BeliefSearchPolice
    BeliefUsage = BeliefUsage
    CurrentScentBelief = CurrentScentBelief
    DeterministicSearchPolice = DeterministicSearchPolice
    FEATURES = FEATURES
    LookaheadEvasionThief = LookaheadEvasionThief
    OpponentModel = OpponentModel
    PartitionPolice = PartitionPolice
    RandomLegalPolice = RandomLegalPolice
    RandomLegalThief = RandomLegalThief
    ScentEvasionThief = ScentEvasionThief
    ScentGreedyPolice = ScentGreedyPolice
    ScentTacticalPolice = ScentTacticalPolice
    SeparatorPlan = SeparatorPlan
    SeparatorVariant = SeparatorVariant
    SpaceSeekingThief = SpaceSeekingThief
    TacticalOneStepPolice = TacticalOneStepPolice
    TrajectoryBeamBelief = TrajectoryBeamBelief
    blocked = staticmethod(blocked)
    manhattan = staticmethod(manhattan)
    modeled_replies = staticmethod(modeled_replies)
    neighbours = staticmethod(neighbours)
    plan_separator = staticmethod(plan_separator)
    reachable_area = staticmethod(reachable_area)
    scent_weights = staticmethod(scent_weights)
    target_of = staticmethod(target_of)
