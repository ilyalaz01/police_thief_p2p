"""Validate two peer results and extract one symmetric outer-series row."""

from __future__ import annotations

import json
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from ..interop.artifacts import consensus_sha256, final_consensus_scope, score_sub_game
from ..interop.profile import MatchProfile
from .series import SeriesSlot


def _artifact_objects(result: dict[str, Any]) -> dict[str, dict[str, Any]]:
    """Load the exact four ephemeral schema-1.1 artifacts from one peer result."""
    paths = result.get("artifacts")
    if not isinstance(paths, list) or len(paths) != 4:
        raise ValueError("localhost peer did not produce four artifacts")
    objects: dict[str, dict[str, Any]] = {}
    for raw in paths:
        path = Path(raw)
        try:
            value = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError) as exc:
            raise ValueError("localhost peer artifact is unreadable") from exc
        objects[path.name.split("_", 1)[0]] = value
    if set(objects) != {"declaration", "config", "log", "result"}:
        raise ValueError("localhost peer artifact set is incomplete")
    if any(value.get("schema_version") != "1.1" for value in objects.values()):
        raise ValueError("localhost peer artifact schema is not 1.1")
    return objects


def _peer_check(
    slot: SeriesSlot, group_id: str, result: dict[str, Any], profile: MatchProfile
) -> dict[str, Any]:
    """Reject a failed audit/replay and return only sanitized inspectable facts."""
    audit = result.get("audit")
    replay = result.get("replay")
    if (
        result.get("ok") is not True
        or result.get("phase") != "verified"
        or result.get("config_sha256") != profile.sha256
        or not isinstance(audit, dict)
        or audit.get("verified") is not True
        or not isinstance(replay, dict)
        or replay.get("verified") is not True
    ):
        raise ValueError("localhost sub-game requires a verified peer result")
    return {
        "sub_game_number": slot.sub_game_number,
        "group_id": group_id,
        "role": slot.roles[group_id],
        "audit_verified": True,
        "replay_verified": True,
        "records": result.get("records"),
        "config_sha256": result["config_sha256"],
    }


def extract_pair_evidence(
    slot: SeriesSlot,
    results: Mapping[str, dict[str, Any]],
    profile: MatchProfile,
    commits: Mapping[str, str],
    game_id: str,
) -> tuple[dict[str, Any], dict[str, dict[str, Any]], tuple[dict[str, Any], ...]]:
    """Return one verified series row, two log summaries, and sanitized checks."""
    groups = tuple(sorted(slot.roles))
    if set(results) != set(groups):
        raise ValueError("localhost peer result groups differ from the sealed slot")
    checks = tuple(_peer_check(slot, group, results[group], profile) for group in groups)
    artifacts = {group: _artifact_objects(results[group]) for group in groups}
    source_rows = {group: artifacts[group]["result"]["sub_games"] for group in groups}
    if any(not isinstance(rows, list) or len(rows) != 1 for rows in source_rows.values()):
        raise ValueError("localhost peer result must contain one sub-game")
    rows = {group: source_rows[group][0] for group in groups}
    scopes = {
        group: final_consensus_scope(
            artifacts[group]["result"]["game_id"],
            {
                key: artifacts[group]["result"]["final_result"][key]
                for key in ("total_score", "sub_games_won", "ties", "winner_group", "series_tie")
            },
            [rows[group]],
        )
        for group in groups
    }
    mutual = {
        group: artifacts[group]["result"]["mutual_agreement"]["sha256"] for group in groups
    }
    if (
        scopes[groups[0]] != scopes[groups[1]]
        or any(consensus_sha256(scopes[group]) != mutual[group] for group in groups)
    ):
        raise ValueError("localhost peers disagree on the single-game consensus scope")
    source = rows[groups[0]]
    outcome = source.get("result")
    expected_score = score_sub_game(outcome, slot.roles)
    winner_role = "police" if outcome == "capture" else "thief"
    winner_group = next(group for group in groups if slot.roles[group] == winner_role)
    if (
        outcome not in {"capture", "survival"}
        or source.get("roles") != slot.roles
        or source.get("score") != expected_score
        or source.get("winner_group") != winner_group
    ):
        raise ValueError("localhost sub-game outcome differs from official scoring")
    logs = {
        group: dict(
            artifacts[group]["log"]["summary"],
            records=artifacts[group]["log"]["records"],
        )
        for group in groups
    }
    for summary in logs.values():
        if summary.get("audit", {}).get("passed") is not True:
            raise ValueError("localhost sub-game log audit did not pass")
        summary["sub_game_number"] = slot.sub_game_number
        summary["winner"] = summary.pop("winner_role")
    row = {
        "sub_game_number": slot.sub_game_number,
        "roles": slot.roles,
        "started_at": source["started_at"],
        "ended_at": source["ended_at"],
        "result": outcome,
        "winner_group": winner_group,
        "github_commit": dict(commits),
        "tokens": dict.fromkeys(groups, 0),
        "score": expected_score,
        "log_files": {
            group: f"{group}/log_{game_id}_g{slot.sub_game_number:02d}.json"
            for group in groups
        },
        "audit": {"log_verified": True, "tampered": False},
    }
    return row, logs, checks
