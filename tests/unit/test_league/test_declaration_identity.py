"""Contract tests for final declaration identity and per-game provenance."""

from __future__ import annotations

import pytest

from police_thief_lab.league.identity import (
    HardwareIdentity,
    TeamDeclarationIdentity,
    validate_series_commits,
)
from tests.support.league_fixtures import GROUP_A, GROUP_B


def _identity(group_id: str = GROUP_A) -> TeamDeclarationIdentity:
    return TeamDeclarationIdentity(
        group_id=group_id,
        group_name="Alpha Team",
        members=("Student One", "Student Two"),
        cop_repo="https://github.com/example/cop",
        thief_repo="https://github.com/example/thief",
        cop_mcp_url="https://cop.example/mcp",
        thief_mcp_url="https://thief.example/mcp",
        llm_model="deterministic-python",
        hardware=HardwareIdentity("CPU", 3200, 8, 16, "none", 0),
    )


def test_identity_maps_to_the_existing_declaration_builder_shape() -> None:
    value = _identity().object()
    assert value["group_id"] == GROUP_A
    assert value["repos"] == {
        "cop": "https://github.com/example/cop",
        "thief": "https://github.com/example/thief",
    }
    assert value["mcp_servers"]["cop"].endswith("/mcp")
    assert value["spec"]["cpu_cores"] == 8


@pytest.mark.parametrize("group_id", ["short", "ninechars", "bad id00"])
def test_group_id_must_be_exactly_eight_characters_without_spaces(group_id: str) -> None:
    with pytest.raises(ValueError, match="group_id"):
        _identity(group_id)


def test_final_identity_refuses_missing_members_and_non_github_repositories() -> None:
    with pytest.raises(ValueError, match="members"):
        TeamDeclarationIdentity(
            group_id=GROUP_A,
            group_name="Alpha Team",
            members=(),
            cop_repo="https://github.com/example/cop",
            thief_repo="https://github.com/example/thief",
            cop_mcp_url="https://cop.example/mcp",
            thief_mcp_url="https://thief.example/mcp",
            llm_model="model",
            hardware=HardwareIdentity("CPU", 3200, 8, 16, "none", 0),
        )
    with pytest.raises(ValueError, match="GitHub"):
        _identity().__class__(
            group_id=GROUP_A,
            group_name="Alpha Team",
            members=("Student",),
            cop_repo="https://example.com/cop",
            thief_repo="https://github.com/example/thief",
            cop_mcp_url="https://cop.example/mcp",
            thief_mcp_url="https://thief.example/mcp",
            llm_model="model",
            hardware=HardwareIdentity("CPU", 3200, 8, 16, "none", 0),
        )


def test_six_sub_game_commits_are_complete_and_preserved_as_opaque_values() -> None:
    commits = {
        number: {GROUP_A: f"alpha-opaque-{number}", GROUP_B: f"bravo-opaque-{number}"}
        for number in range(1, 7)
    }
    assert validate_series_commits(commits, [GROUP_A, GROUP_B]) == commits
    commits[4][GROUP_B] = "UNRESOLVED_SELF_TEST_NO_GIT_METADATA"
    with pytest.raises(ValueError, match="unresolved"):
        validate_series_commits(commits, [GROUP_A, GROUP_B])
