"""Offline six-sub-game scheduling, coordination, and raw aggregation."""

from __future__ import annotations

import copy
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from typing import Any

from ..interop.artifacts import derive_game_ids, score_sub_game
from ..interop.profile import MatchProfile
from .identity import validate_group_id

KIT_SORTED_FIRST_POLICE_ODD_V1 = "kit_sorted_first_police_odd_v1"
BLOCKED_TIE_STATUS = "BLOCKED_PENDING_EXPLICIT_BILATERAL_TIE_POLICY"
FINAL_NO_TIE_STATUS = "FINAL_NO_SERIES_TIE_POLICY_NEEDED"


@dataclass(frozen=True, slots=True)
class SeriesSlot:
    """One sealed role assignment in the fixed six-sub-game schedule."""

    sub_game_number: int
    police_group: str
    thief_group: str

    @property
    def roles(self) -> dict[str, str]:
        """Return the group-to-role mapping expected by existing artifacts."""
        return {self.police_group: "police", self.thief_group: "thief"}


def _two_groups(group_ids: Sequence[str]) -> tuple[str, str]:
    """Validate and return the two unique group IDs in canonical order."""
    groups = tuple(group_ids)
    if len(groups) != 2 or len(set(groups)) != 2:
        raise ValueError("series requires exactly two distinct groups")
    for group_id in groups:
        validate_group_id(group_id)
    return tuple(sorted(groups))


def series_reference_terms(profile: MatchProfile) -> dict[str, Any]:
    """Create the flat fourteen terms for a series without mutating one-game behavior."""
    return profile.reference_terms() | {"num_games": 6}


def derive_series_game_ids(
    profile: MatchProfile, group_a: str, group_b: str
) -> tuple[str, str]:
    """Derive identifiers only from the flat fourteen terms and sorted groups."""
    return derive_game_ids(series_reference_terms(profile), group_a, group_b)


def build_series_schedule(
    group_ids: Sequence[str], *, local_profile: str, peer_profile: str,
    bilateral_approval_recorded: bool,
) -> tuple[SeriesSlot, ...]:
    """Build six alternating slots only after explicit matching-profile approval."""
    if local_profile != peer_profile:
        raise ValueError("role schedule profiles differ")
    if local_profile != KIT_SORTED_FIRST_POLICE_ODD_V1:
        raise ValueError("unsupported role schedule profile")
    if bilateral_approval_recorded is not True:
        raise ValueError("explicit bilateral role schedule approval is required")
    first, second = _two_groups(group_ids)
    return tuple(
        SeriesSlot(number, first, second) if number % 2 else SeriesSlot(number, second, first)
        for number in range(1, 7)
    )


def _validate_schedule(schedule: Sequence[SeriesSlot]) -> None:
    """Refuse an altered or incomplete sealed schedule."""
    if len(schedule) != 6 or [slot.sub_game_number for slot in schedule] != list(range(1, 7)):
        raise ValueError("offline coordinator requires sealed sub-games 1 through 6")
    groups = [schedule[0].police_group, schedule[0].thief_group]
    expected = build_series_schedule(
        groups, local_profile=KIT_SORTED_FIRST_POLICE_ODD_V1,
        peer_profile=KIT_SORTED_FIRST_POLICE_ODD_V1, bilateral_approval_recorded=True,
    )
    if tuple(schedule) != expected:
        raise ValueError("offline coordinator role schedule mismatch")


def coordinate_offline_series(
    schedule: Sequence[SeriesSlot], runner: Callable[[SeriesSlot], dict[str, Any]]
) -> tuple[dict[str, Any], ...]:
    """Invoke an injected local runner exactly once per sealed slot and validate identity."""
    _validate_schedule(schedule)
    rows = []
    for slot in schedule:
        row = runner(slot)
        if not isinstance(row, dict):
            raise ValueError("offline sub-game runner must return an object")
        if row.get("sub_game_number") != slot.sub_game_number or row.get("roles") != slot.roles:
            raise ValueError("offline sub-game identity disagrees with sealed slot")
        rows.append(copy.deepcopy(row))
    return tuple(rows)


def aggregate_series_rows(
    rows: Sequence[dict[str, Any]], group_ids: Sequence[str]
) -> dict[str, Any]:
    """Aggregate six scored rows while leaving a tied-series policy explicitly blocked."""
    groups = _two_groups(group_ids)
    if any(not isinstance(row, dict) for row in rows):
        raise ValueError("aggregate rows must be objects")
    numbers = [row.get("sub_game_number") for row in rows]
    if len(rows) != 6 or numbers != list(range(1, 7)):
        raise ValueError("aggregate requires exactly the six numbered sub-games")
    totals = dict.fromkeys(groups, 0)
    wins = dict.fromkeys(groups, 0)
    ties = 0
    for row in rows:
        roles = row.get("roles")
        if (
            not isinstance(roles, dict) or set(roles) != set(groups)
            or set(roles.values()) != {"police", "thief"}
        ):
            raise ValueError("sub-game role mapping mismatch")
        result = row.get("result")
        if result not in {"capture", "survival"}:
            raise ValueError("sub-game outcome scoring requires a separately agreed profile")
        score = row.get("score")
        if not isinstance(score, dict) or set(score) != set(groups):
            raise ValueError("sub-game score groups mismatch")
        if any(isinstance(value, bool) or not isinstance(value, int) or value < 0
               for value in score.values()):
            raise ValueError("sub-game scores must be non-negative integers")
        if score != score_sub_game(result, roles):
            raise ValueError("sub-game score differs from the official role score")
        expected_winner = next(group for group in groups if roles[group] == (
            "police" if result == "capture" else "thief"
        ))
        if row.get("winner_group") != expected_winner:
            raise ValueError("sub-game winner differs from the official outcome")
        for group in groups:
            totals[group] += score[group]
        top = max(score.values())
        row_winners = [group for group in groups if score[group] == top]
        if len(row_winners) == 1:
            wins[row_winners[0]] += 1
        else:
            ties += 1
    leaders = [group for group in groups if totals[group] == max(totals.values())]
    series_tie = len(leaders) != 1
    return {
        "total_score": totals, "sub_games_won": wins, "ties": ties,
        "winner_group": None if series_tie else leaders[0], "series_tie": series_tie,
        "settlement_status": BLOCKED_TIE_STATUS if series_tie else FINAL_NO_TIE_STATUS,
    }


def series_token_totals(
    rows: Sequence[dict[str, Any]], group_ids: Sequence[str]
) -> dict[str, int]:
    """Sum truthful non-negative integer token counts across exactly six rows."""
    groups = _two_groups(group_ids)
    if len(rows) != 6:
        raise ValueError("token totals require exactly six sub-games")
    totals = dict.fromkeys(groups, 0)
    for row in rows:
        tokens = row.get("tokens") if isinstance(row, dict) else None
        if not isinstance(tokens, dict) or set(tokens) != set(groups):
            raise ValueError("sub-game token groups mismatch")
        if any(isinstance(value, bool) or not isinstance(value, int) or value < 0
               for value in tokens.values()):
            raise ValueError("sub-game token counts must be non-negative integers")
        for group in groups:
            totals[group] += tokens[group]
    return totals
