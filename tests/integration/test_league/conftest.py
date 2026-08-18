"""Local-only fixtures for six-game runtime integration tests."""

from pathlib import Path

import pytest

from police_thief_lab.interop.profile import MatchProfile
from police_thief_lab.league import (
    APPENDIX_B_CANONICAL_COMPACT_V1,
    KIT_SORTED_FIRST_POLICE_ODD_V1,
    HardwareIdentity,
    LocalhostSeriesRequest,
    TeamDeclarationIdentity,
    build_appendix_b_candidate,
    build_series_schedule,
    confirm_appendix_b_lock,
)
from tests.support.league_fixtures import GROUP_A, GROUP_B, appendix_b_config


def _identity(group_id: str) -> TeamDeclarationIdentity:
    """Return a syntactically complete, explicitly non-operational team identity."""
    return TeamDeclarationIdentity(
        group_id=group_id,
        group_name=f"Local fixture {group_id}",
        members=("Local Test Operator",),
        cop_repo=f"https://github.com/example/{group_id}-police",
        thief_repo=f"https://github.com/example/{group_id}-thief",
        cop_mcp_url=f"https://{group_id}-police.invalid/mcp",
        thief_mcp_url=f"https://{group_id}-thief.invalid/mcp",
        llm_model="deterministic-python",
        hardware=HardwareIdentity("local-test-cpu", 1.0, 1, 1.0, "none", 0.0),
    )


@pytest.fixture
def localhost_series_request(tmp_path: Path) -> LocalhostSeriesRequest:
    """Build a synthetic approved plan used only by the localhost self-test."""
    candidate = build_appendix_b_candidate(
        appendix_b_config(), serialization_profile=APPENDIX_B_CANONICAL_COMPACT_V1
    )
    lock = confirm_appendix_b_lock(
        candidate,
        peer_sha256=candidate.sha256,
        peer_serialization_profile=candidate.serialization_profile,
        bilateral_approval_recorded=True,
    )
    profile = MatchProfile(
        board_config={
            "board_size": 7,
            "police_start": [0, 0],
            "thief_start": [3, 3],
            "blocked_cells": [],
            "barrier_quota": 14,
        },
        survival_limit=35,
        move_limit=35,
        timeouts={"connect": 5.0, "turn": 5.0, "audit": 5.0, "retry": 0.01},
        artifact_profile="reference-v3-artifact-1.1",
        artifact_schema="1.1",
        consensus_scope="reference_symmetric_outcome_without_tie",
        setting="New York",
        minimum_center_intensity=0.5,
        step_numbering="sender_local",
    )
    schedule = build_series_schedule(
        [GROUP_A, GROUP_B],
        local_profile=KIT_SORTED_FIRST_POLICE_ODD_V1,
        peer_profile=KIT_SORTED_FIRST_POLICE_ODD_V1,
        bilateral_approval_recorded=True,
    )
    commits = {
        number: {GROUP_A: f"local-alpha-{number}", GROUP_B: f"local-bravo-{number}"}
        for number in range(1, 7)
    }
    return LocalhostSeriesRequest(
        profile=profile,
        config_lock=lock,
        schedule=schedule,
        identities=(_identity(GROUP_A), _identity(GROUP_B)),
        commits=commits,
        output_dir=tmp_path / "series",
        max_tokens_per_game=200_000,
    )
