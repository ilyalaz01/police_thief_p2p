"""Explicit runtime policy selection for the negotiable Thief role."""

from __future__ import annotations

from ..policies.baselines import RandomLegalThief, SpaceSeekingThief
from ..policies.strong_thieves import (
    BarrierAwareThief,
    LookaheadEvasionThief,
    ScentEvasionThief,
)
from ..simulator import DecisionBackend

DEFAULT_THIEF_POLICY = "RandomLegalThief"
THIEF_POLICIES = {
    "RandomLegalThief": RandomLegalThief,
    "SpaceSeekingThief": SpaceSeekingThief,
    "BarrierAwareThief": BarrierAwareThief,
    "ScentEvasionThief": ScentEvasionThief,
    "LookaheadEvasionThief": LookaheadEvasionThief,
}


def thief_policy_names() -> tuple[str, ...]:
    """Return the selectable Thief policy names in their documented order."""
    return tuple(THIEF_POLICIES)


def build_thief_backend(name: str | None, seed: int) -> DecisionBackend:
    """Build one seeded Thief backend, refusing an unknown policy name."""
    selected = name or DEFAULT_THIEF_POLICY
    if selected not in THIEF_POLICIES:
        raise ValueError(
            f"unsupported thief policy {selected!r}; choose one of {sorted(THIEF_POLICIES)}"
        )
    return THIEF_POLICIES[selected](seed)
