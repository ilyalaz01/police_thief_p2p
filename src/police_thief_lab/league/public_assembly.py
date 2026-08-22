"""File-oriented entry point that turns six public sub-game results into one bundle."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from ..interop.profile import MatchProfile
from .config import (
    APPENDIX_B_CANONICAL_COMPACT_V1,
    LOCKED_BILATERAL_APPROVAL,
    AppendixBConfigLock,
    build_appendix_b_candidate,
)
from .declaration_input import load_declaration_identity
from .public_series import extract_own_row, write_own_series_bundle
from .series import (
    KIT_SORTED_FIRST_POLICE_ODD_V1,
    aggregate_series_rows,
    build_series_schedule,
    derive_series_game_ids,
    series_token_totals,
)


def _lock(path: Path) -> AppendixBConfigLock:
    """Read the agreed Appendix-B configuration exactly as both teams hold it."""
    value = json.loads(Path(path).read_text(encoding="utf-8"))
    candidate = build_appendix_b_candidate(
        value, serialization_profile=APPENDIX_B_CANONICAL_COMPACT_V1
    )
    return AppendixBConfigLock(
        candidate.bytes, candidate.sha256, candidate.scope,
        candidate.serialization_profile, LOCKED_BILATERAL_APPROVAL,
    )


def assemble_public_series(
    our_declaration: Path,
    peer_declaration: Path,
    appendix_b: Path,
    profile: Path,
    results: tuple[Path, ...],
    out: Path,
    max_tokens_per_game: int = 0,
) -> dict[str, Any]:
    """Verify six own-side sub-games, aggregate them, and write our counted bundle."""
    own = load_declaration_identity(our_declaration)
    peer = load_declaration_identity(peer_declaration)
    if own.group_id == peer.group_id:
        raise ValueError("the two declarations carry the same group id")
    match_profile = MatchProfile(**json.loads(Path(profile).read_text(encoding="utf-8")))
    groups = tuple(sorted({own.group_id, peer.group_id}))
    schedule = build_series_schedule(
        groups, local_profile=KIT_SORTED_FIRST_POLICE_ODD_V1,
        peer_profile=KIT_SORTED_FIRST_POLICE_ODD_V1, bilateral_approval_recorded=True,
    )
    game_id, game_uid = derive_series_game_ids(match_profile, *groups)
    rows, logs, checks = [], {}, []
    for slot, path in zip(schedule, results, strict=True):
        result = json.loads(Path(path).read_text(encoding="utf-8"))
        row, summary, check = extract_own_row(slot, result, match_profile, game_id)
        rows.append(row)
        logs[slot.sub_game_number] = summary
        checks.append(check)
    aggregate = aggregate_series_rows(rows, groups)
    tokens = series_token_totals(rows, groups)
    paths, mutual = write_own_series_bundle(
        Path(out), game_id, game_uid, match_profile, _lock(appendix_b), own, peer,
        tuple(rows), aggregate, logs, max_tokens_per_game,
    )
    return {
        "game_id": game_id,
        "game_uid": game_uid,
        "our_group_id": own.group_id,
        "role_schedule": [
            {"sub_game_number": slot.sub_game_number, **slot.roles} for slot in schedule
        ],
        "aggregate": aggregate,
        "token_totals": tokens,
        "series_consensus_sha256": mutual,
        "sub_game_consensus_sha256": {
            check["sub_game_number"]: check["sub_game_consensus_sha256"] for check in checks
        },
        "shared_config_sha256": _lock(appendix_b).sha256,
        "config_path": str(paths[0]),
        "result_path": str(paths[1]),
        "mailed": False,
    }
