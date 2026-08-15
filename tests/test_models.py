"""Validation tests for immutable Phase 1 domain models."""

from dataclasses import FrozenInstanceError

import pytest

from police_thief_lab import Action, Direction, GameConfig, MoveType, Position
from police_thief_lab.models import StartValidationProfile


def test_action_constructors_are_typed() -> None:
    """Each action constructor produces one unambiguous action shape."""
    assert Action.move(Direction.N) == Action(MoveType.MOVE, Direction.N)
    assert Action.stay() == Action(MoveType.STAY, Direction.STAY)
    assert Action.barrier(Position(1, 2)) == Action(
        MoveType.BARRIER, barrier_position=Position(1, 2)
    )


def test_domain_values_are_immutable() -> None:
    """Policies cannot mutate coordinates they receive."""
    position = Position(1, 2)
    with pytest.raises(FrozenInstanceError):
        position.row = 3  # type: ignore[misc]


@pytest.mark.parametrize(
    ("override", "message"),
    [
        ({"board_size": 6}, "board_size"),
        ({"barrier_quota": 13}, "barrier_quota"),
        ({"survival_threshold": 34}, "survival_threshold"),
        ({"police_start": Position(-1, 0)}, "in bounds"),
        ({"blocked_cells": frozenset({Position(0, 0)})}, "blocked cell"),
    ],
)
def test_config_enforces_appendix_f_and_geometry(override: dict, message: str) -> None:
    """Shared config cannot lower mandatory minima or start in invalid terrain."""
    with pytest.raises(ValueError, match=message):
        GameConfig(**override)


def test_shared_start_is_interop_valid_but_lab_profile_can_reject() -> None:
    """Start separation is an explicit laboratory option, not an official invariant."""
    assert GameConfig(thief_start=Position(0, 0)).police_start == Position(0, 0)
    with pytest.raises(ValueError, match="lab_distinct"):
        GameConfig(
            thief_start=Position(0, 0), start_validation_profile=StartValidationProfile.LAB_DISTINCT
        )
