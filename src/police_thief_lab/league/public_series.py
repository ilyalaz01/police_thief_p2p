"""Assemble one team's counted-series bundle from its own six public sub-game results."""

from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from ..interop.artifacts import (
    build_config_artifact,
    build_declaration,
    build_log,
    build_result,
    consensus_sha256,
    final_consensus_scope,
    pretty_bytes,
    score_sub_game,
)
from ..interop.profile import MatchProfile
from .config import AppendixBConfigLock
from .identity import TeamDeclarationIdentity
from .series import SeriesSlot, series_reference_terms

AGGREGATE_FIELDS = ("total_score", "sub_games_won", "ties", "winner_group", "series_tie")


def _artifacts(result: Mapping[str, Any]) -> dict[str, dict[str, Any]]:
    """Load the four schema-1.1 artifacts one of our peer runs retained."""
    paths = result.get("artifacts")
    if not isinstance(paths, list) or len(paths) != 4:
        raise ValueError("a public sub-game result must reference four artifacts")
    objects: dict[str, dict[str, Any]] = {}
    for raw in paths:
        path = Path(raw)
        try:
            objects[path.name.split("_", 1)[0]] = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError) as exc:
            raise ValueError(f"sub-game artifact is unreadable: {path.name}") from exc
    if set(objects) != {"declaration", "config", "log", "result"}:
        raise ValueError("sub-game artifact set is incomplete")
    if any(value.get("schema_version") != "1.1" for value in objects.values()):
        raise ValueError("sub-game artifact schema is not 1.1")
    return objects


def _require_verified(slot: SeriesSlot, result: Mapping[str, Any], profile: MatchProfile) -> None:
    """Refuse any sub-game our own peer did not finish, audit and replay cleanly."""
    audit, replay = result.get("audit"), result.get("replay")
    if (
        result.get("ok") is not True
        or result.get("phase") != "verified"
        or result.get("config_sha256") != profile.sha256
        or not isinstance(audit, dict) or audit.get("verified") is not True
        or not isinstance(replay, dict) or replay.get("verified") is not True
    ):
        raise ValueError(f"sub-game {slot.sub_game_number} is not a verified peer result")


def extract_own_row(
    slot: SeriesSlot, result: Mapping[str, Any], profile: MatchProfile, game_id: str
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    """Return one series row, our log summary, and the sanitized per-game check."""
    _require_verified(slot, result, profile)
    artifacts = _artifacts(result)
    rows = artifacts["result"]["sub_games"]
    if not isinstance(rows, list) or len(rows) != 1:
        raise ValueError(f"sub-game {slot.sub_game_number} must report exactly one sub-game")
    source = rows[0]
    outcome = source.get("result")
    if outcome not in {"capture", "survival"}:
        raise ValueError(f"sub-game {slot.sub_game_number} outcome is not officially scored")
    if source.get("roles") != slot.roles:
        raise ValueError(f"sub-game {slot.sub_game_number} roles differ from the sealed schedule")
    expected_score = score_sub_game(outcome, slot.roles)
    winner_role = "police" if outcome == "capture" else "thief"
    winner_group = next(g for g in slot.roles if slot.roles[g] == winner_role)
    if source.get("score") != expected_score or source.get("winner_group") != winner_group:
        raise ValueError(f"sub-game {slot.sub_game_number} scoring differs from the official table")
    summary = dict(artifacts["log"]["summary"], records=artifacts["log"]["records"])
    if summary.get("audit", {}).get("passed") is not True:
        raise ValueError(f"sub-game {slot.sub_game_number} log audit did not pass")
    summary["sub_game_number"] = slot.sub_game_number
    summary["winner"] = summary.pop("winner_role")
    row = {
        "sub_game_number": slot.sub_game_number,
        "roles": dict(slot.roles),
        "started_at": source["started_at"],
        "ended_at": source["ended_at"],
        "result": outcome,
        "winner_group": winner_group,
        "github_commit": dict(source["github_commit"]),
        "tokens": dict(source["tokens"]),
        "score": expected_score,
        "log_files": {
            group: f"{group}/artifacts/log_{game_id}_g{slot.sub_game_number:02d}.json"
            for group in sorted(slot.roles)
        },
        "audit": {"log_verified": True, "tampered": False},
    }
    check = {
        "sub_game_number": slot.sub_game_number,
        "role": slot.roles[min(slot.roles)],
        "records": result.get("records"),
        "sub_game_consensus_sha256": artifacts["result"]["mutual_agreement"]["sha256"],
        "config_sha256": result["config_sha256"],
    }
    return row, summary, check


def write_own_series_bundle(
    root: Path,
    game_id: str,
    game_uid: str,
    profile: MatchProfile,
    lock: AppendixBConfigLock,
    own: TeamDeclarationIdentity,
    peer: TeamDeclarationIdentity,
    rows: Sequence[dict[str, Any]],
    aggregate: Mapping[str, Any],
    logs: Mapping[int, dict[str, Any]],
    max_tokens_per_game: int,
) -> tuple[tuple[Path, Path], str]:
    """Write this team's own counted-series bundle and return the mutual result hash."""
    groups = tuple(sorted({own.group_id, peer.group_id}))
    artifact_aggregate = {field: aggregate[field] for field in AGGREGATE_FIELDS}
    mutual = consensus_sha256(final_consensus_scope(game_id, artifact_aggregate, list(rows)))
    directory = root / "artifacts"
    directory.mkdir(parents=True, exist_ok=True)
    (root / "config").mkdir(parents=True, exist_ok=True)
    (root / "config/game.json").write_bytes(lock.bytes)
    times = (rows[0]["started_at"], rows[-1]["ended_at"])
    declaration = build_declaration(
        game_id, game_uid, "Asia/Jerusalem", *times, 6, max_tokens_per_game,
        own.object(), peer.object(),
    )
    (directory / f"declaration_{game_id}.json").write_bytes(pretty_bytes(declaration))
    for number in range(1, 7):
        config = build_config_artifact(series_reference_terms(profile), game_id, game_uid, number)
        (directory / f"config_{game_id}_g{number:02d}.json").write_bytes(pretty_bytes(config))
        log = build_log(dict(logs[number]), game_id, game_uid, own.group_id, peer.group_id)
        (directory / f"log_{game_id}_g{number:02d}.json").write_bytes(pretty_bytes(log))
    result = build_result(game_id, game_uid, groups, list(rows), artifact_aggregate, mutual)
    result_path = directory / f"result_{game_id}.json"
    result_path.write_bytes(pretty_bytes(result))
    return (root / "config/game.json", result_path), mutual
