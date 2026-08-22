"""Contract tests for six-game scheduling, coordination, and aggregation."""

from __future__ import annotations

import pytest

from police_thief_lab.interop.artifacts import derive_game_ids
from police_thief_lab.interop.profile import MatchProfile
from police_thief_lab.league.series import (
    KIT_SORTED_FIRST_POLICE_ODD_V1,
    aggregate_series_rows,
    build_series_schedule,
    coordinate_offline_series,
    derive_series_game_ids,
    series_reference_terms,
    series_token_totals,
)
from tests.support.league_fixtures import GROUP_A, GROUP_B


def _profile() -> MatchProfile:
    return MatchProfile(
        board_config={
            "board_size": 7,
            "police_start": [0, 0],
            "thief_start": [3, 3],
            "barrier_quota": 14,
        }
    )


def test_series_terms_change_only_num_games_outside_match_profile() -> None:
    profile = _profile()
    single = profile.reference_terms()
    series = series_reference_terms(profile)
    assert single["num_games"] == 1
    assert series == single | {"num_games": 6}
    assert profile.reference_terms() == single


def test_series_uid_uses_flat_fourteen_terms_not_the_appendix_b_object() -> None:
    profile = _profile()
    expected = derive_game_ids(series_reference_terms(profile), GROUP_A, GROUP_B)
    assert derive_series_game_ids(profile, GROUP_B, GROUP_A) == expected


def test_six_game_schedule_is_explicitly_approved_and_alternates_roles() -> None:
    with pytest.raises(ValueError, match="bilateral"):
        build_series_schedule(
            [GROUP_B, GROUP_A],
            local_profile=KIT_SORTED_FIRST_POLICE_ODD_V1,
            peer_profile=KIT_SORTED_FIRST_POLICE_ODD_V1,
            bilateral_approval_recorded=False,
        )
    schedule = build_series_schedule(
        [GROUP_B, GROUP_A],
        local_profile=KIT_SORTED_FIRST_POLICE_ODD_V1,
        peer_profile=KIT_SORTED_FIRST_POLICE_ODD_V1,
        bilateral_approval_recorded=True,
    )
    assert [slot.sub_game_number for slot in schedule] == list(range(1, 7))
    assert [slot.police_group for slot in schedule] == [
        GROUP_A, GROUP_B, GROUP_A, GROUP_B, GROUP_A, GROUP_B
    ]
    assert all(slot.roles[slot.police_group] == "police" for slot in schedule)


def test_schedule_refuses_differing_role_profiles() -> None:
    with pytest.raises(ValueError, match="role schedule"):
        build_series_schedule(
            [GROUP_A, GROUP_B],
            local_profile=KIT_SORTED_FIRST_POLICE_ODD_V1,
            peer_profile="opponent-different-order",
            bilateral_approval_recorded=True,
        )


def test_offline_coordinator_runs_exactly_six_slots_and_validates_rows() -> None:
    schedule = build_series_schedule(
        [GROUP_A, GROUP_B],
        local_profile=KIT_SORTED_FIRST_POLICE_ODD_V1,
        peer_profile=KIT_SORTED_FIRST_POLICE_ODD_V1,
        bilateral_approval_recorded=True,
    )
    called: list[int] = []

    def runner(slot: object) -> dict[str, object]:
        called.append(slot.sub_game_number)
        return {
            "sub_game_number": slot.sub_game_number,
            "roles": slot.roles,
            "result": "capture",
            "winner_group": slot.police_group,
            "score": {slot.police_group: 20, slot.thief_group: 5},
            "tokens": {GROUP_A: 10, GROUP_B: 20},
        }

    rows = coordinate_offline_series(schedule, runner)
    assert called == list(range(1, 7))
    aggregate = aggregate_series_rows(rows, [GROUP_A, GROUP_B])
    assert aggregate == {
        "total_score": {GROUP_A: 75, GROUP_B: 75},
        "sub_games_won": {GROUP_A: 3, GROUP_B: 3},
        "ties": 0,
        "winner_group": None,
        "series_tie": True,
        "settlement_status": "FINAL_OFFICIAL_TIE_SCORE_APPLIED",
        "series_tie_score": {GROUP_A: 2, GROUP_B: 2},
    }
    assert series_token_totals(rows, [GROUP_A, GROUP_B]) == {GROUP_A: 60, GROUP_B: 120}


def test_coordinator_rejects_a_row_that_disagrees_with_the_sealed_slot() -> None:
    schedule = build_series_schedule(
        [GROUP_A, GROUP_B],
        local_profile=KIT_SORTED_FIRST_POLICE_ODD_V1,
        peer_profile=KIT_SORTED_FIRST_POLICE_ODD_V1,
        bilateral_approval_recorded=True,
    )

    def wrong(slot: object) -> dict[str, object]:
        return {"sub_game_number": 99, "roles": slot.roles, "score": {}}

    with pytest.raises(ValueError, match="sub-game identity"):
        coordinate_offline_series(schedule, wrong)


def test_aggregate_refuses_non_official_scores() -> None:
    schedule = build_series_schedule(
        [GROUP_A, GROUP_B],
        local_profile=KIT_SORTED_FIRST_POLICE_ODD_V1,
        peer_profile=KIT_SORTED_FIRST_POLICE_ODD_V1,
        bilateral_approval_recorded=True,
    )
    rows = [
        {
            "sub_game_number": slot.sub_game_number,
            "roles": slot.roles,
            "result": "capture",
            "winner_group": slot.police_group,
            "score": {slot.police_group: 20, slot.thief_group: 5},
        }
        for slot in schedule
    ]
    rows[2]["score"][schedule[2].police_group] = 19
    with pytest.raises(ValueError, match="official role score"):
        aggregate_series_rows(rows, [GROUP_A, GROUP_B])


def test_token_totals_refuse_missing_or_non_integer_counts() -> None:
    rows = [
        {"tokens": {GROUP_A: number, GROUP_B: number + 1}}
        for number in range(1, 7)
    ]
    rows[3]["tokens"][GROUP_B] = 1.5
    with pytest.raises(ValueError, match="non-negative integers"):
        series_token_totals(rows, [GROUP_A, GROUP_B])
