"""Fail-closed validation for the local six-game series request."""

from __future__ import annotations

import hashlib
import json
from typing import Any

from .config import (
    APPENDIX_B_CANONICAL_COMPACT_V1,
    APPENDIX_B_SCOPE,
    LOCKED_BILATERAL_APPROVAL,
)
from .identity import TeamDeclarationIdentity, validate_series_commits
from .local_models import UNCOUNTED_LOCALHOST_SELF_TEST, LocalhostSeriesRequest
from .series import KIT_SORTED_FIRST_POLICE_ODD_V1, build_series_schedule


def _identity_map(
    identities: tuple[TeamDeclarationIdentity, TeamDeclarationIdentity],
) -> dict[str, TeamDeclarationIdentity]:
    """Return exactly two unique validated identities keyed by group ID."""
    if len(identities) != 2 or any(
        not isinstance(identity, TeamDeclarationIdentity) for identity in identities
    ):
        raise ValueError("localhost series requires two declaration identities")
    output = {identity.group_id: identity for identity in identities}
    if len(output) != 2:
        raise ValueError("localhost series declaration groups must be distinct")
    return output


def _locked_config(request: LocalhostSeriesRequest) -> dict[str, Any]:
    """Verify the named immutable Appendix-B lock before any localhost side effect."""
    lock = request.config_lock
    if (
        lock.scope != APPENDIX_B_SCOPE
        or lock.serialization_profile != APPENDIX_B_CANONICAL_COMPACT_V1
        or lock.approval_status != LOCKED_BILATERAL_APPROVAL
        or hashlib.sha256(lock.bytes).hexdigest() != lock.sha256
    ):
        raise ValueError("localhost series requires a valid Appendix-B byte lock")
    try:
        return json.loads(lock.bytes.decode("utf-8"))
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise ValueError("Appendix-B lock bytes are invalid") from exc


def _validate_profile(request: LocalhostSeriesRequest, config: dict[str, Any]) -> None:
    """Require every directly shared physics field to match the locked full config."""
    profile = request.profile
    board = config["board_and_agents"]
    movement = config["movement_and_barriers"]
    expected = {
        "board_size": board["grid_size"],
        "police_start": board["cop_start"],
        "thief_start": board["thief_start"],
        "barrier_quota": movement["max_barriers"],
    }
    actual = {key: profile.board_config.get(key) for key in expected}
    if actual != expected or profile.move_limit != movement["max_moves"]:
        raise ValueError("MatchProfile physics diverges from the Appendix-B lock")
    if profile.survival_limit != movement["survival_threshold"]:
        raise ValueError("MatchProfile survival threshold diverges from the Appendix-B lock")
    if profile.setting != config["world"]["map_area"]:
        raise ValueError("MatchProfile setting diverges from the Appendix-B lock")
    if (
        profile.artifact_profile != "reference-v3-artifact-1.1"
        or profile.artifact_schema != "1.1"
        or profile.consensus_scope != "reference_symmetric_outcome_without_tie"
    ):
        raise ValueError("localhost series artifact/consensus profile is unsupported")


def validate_localhost_request(
    request: LocalhostSeriesRequest,
) -> tuple[dict[str, TeamDeclarationIdentity], dict[int, dict[str, str]], int]:
    """Validate the complete request and return defensive identity/provenance values."""
    if not isinstance(request, LocalhostSeriesRequest):
        raise ValueError("localhost series request type is invalid")
    if request.classification != UNCOUNTED_LOCALHOST_SELF_TEST:
        raise ValueError("localhost adapter cannot authorize another operation class")
    if request.output_dir.exists():
        raise ValueError("localhost series output must not already exist")
    if (
        isinstance(request.max_tokens_per_game, bool)
        or not isinstance(request.max_tokens_per_game, int)
        or request.max_tokens_per_game <= 0
    ):
        raise ValueError("max_tokens_per_game must be an explicit positive integer")
    config = _locked_config(request)
    identities = _identity_map(request.identities)
    groups = tuple(sorted(identities))
    if set(config["agreed_between"]) != set(groups):
        raise ValueError("Appendix-B and declaration groups differ")
    expected = build_series_schedule(
        groups,
        local_profile=KIT_SORTED_FIRST_POLICE_ODD_V1,
        peer_profile=KIT_SORTED_FIRST_POLICE_ODD_V1,
        bilateral_approval_recorded=True,
    )
    if request.schedule != expected:
        raise ValueError("localhost series schedule differs from the sealed profile")
    _validate_profile(request, config)
    commits = validate_series_commits(request.commits, groups)
    watchdog = int(config["network_and_league"]["watchdog_timeout_sec"])
    return identities, commits, watchdog
