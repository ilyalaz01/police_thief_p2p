"""Reference-compatible artifacts with deliberately separate serialization scopes."""
# ruff: noqa: E501 -- schema prose is pinned verbatim to the professor reference.

from __future__ import annotations

import hashlib
import uuid
from pathlib import Path
from typing import Any

from .artifact_encoding import LINKS_REMARK as LINKS_REMARK
from .artifact_encoding import (
    _ended_at,
    _group,
    artifact_links,
    canonical_sha256,
    consensus_sha256,
    pretty_bytes,
)
from .artifact_encoding import _hardware as _hardware
from .artifact_writers import write_artifacts as write_artifacts
from .crypto import canonical_json

SCHEMA_VERSION = "1.1"
DEFAULT_TIMEZONE = "Asia/Jerusalem"
SCHEMA_DECLARATION = "Static declaration for the WHOLE game (the full series of sub-games) between two teams. This is the single home for every field that does NOT change while the sub-games are played: team identity, members, cop/thief repository URLs, MCP server URLs, hardware spec, LLM model, the agreed max-tokens-per-game cap, and the game start/end times. Roles (cop/thief) switch across the sub-games, so no role and no sub_game_number appear here. Both teams sign it and lock it cryptographically before play (book ch5 Step-0). Data that changes per sub-game (github_commit, moves, scores) lives in 3-game-log.json and 4-final-result.json."
SCHEMA_CONFIG = "Agreed game configuration for one match. Values come from the master parameter table (Appendix F). Per the appendix's mandatory rules both teams must hold BYTE-IDENTICAL values, lock them cryptographically (config_sha256), give the file a unique name per game, and attach it to GitHub. 'status' recap: minimum = may only be raised; permanent = must not change; negotiation = any agreed value."
SCHEMA_LOG = "Per-sub-game match log consumed by the Replay Viewer for cryptographic audit. Each step is committed as SHA-256(State || Move || Intent || Nonce) and later revealed; nonces are revealed only at the final audit (book ch5 commit-reveal, ch7 replay). Static team metadata (hardware, members, repos, model) is NOT repeated here — it lives in 1-pre-game-declaration.json; join by game_uid. Step 0 is the signed step-zero record carrying only what changes per sub-game (github_commit). The 'prompt_discussion' block records the natural-language exchange and the LLM prompt/reasoning behind each hint (book ch6 prompt engineering)."
SCHEMA_RESULT = "Summary and final result for the WHOLE game (all sub-games) between two teams. It condenses the per-sub-game logs into a per-group score for every sub-game plus the aggregate outcome the lecturer needs to build the league standings. Static team metadata (identity, members, repos, MCP, hardware, model) is NOT repeated here — it lives in 1-pre-game-declaration.json and is referenced via game_id / group_id. Both teams must agree on this result and each sends its own copy to the lecturer (book ch9)."
def derive_game_ids(terms: dict[str, Any], group_a: str, group_b: str) -> tuple[str, str]:
    """Derive the pinned shared human id and UUID from negotiated terms and groups."""
    pair = sorted([group_a, group_b])
    game_id = f"{pair[0]}-vs-{pair[1]}"
    seed = f"{canonical_json(terms)}|{'|'.join(pair)}"
    game_uid = str(uuid.UUID(bytes=hashlib.sha256(seed.encode()).digest()[:16]))
    return game_id, game_uid


def score_sub_game(result: str, roles: dict[str, str]) -> dict[str, int]:
    """Apply the official capture/survival scores to a group-to-role mapping."""
    scores = {"capture": {"police": 20, "thief": 5},
              "survival": {"police": 5, "thief": 10}}
    return {group: scores.get(result, {}).get(role, 0) for group, role in roles.items()}


def aggregate_scores(score: dict[str, int]) -> dict[str, Any]:
    """Aggregate the single Phase 4B warm-up sub-game without placeholder values."""
    top = max(score.values())
    winners = [group for group, value in score.items() if value == top]
    tied = len(winners) != 1
    return {
        "total_score": dict(score),
        "sub_games_won": {group: int(not tied and group == winners[0]) for group in score},
        "ties": int(tied),
        "winner_group": None if tied else winners[0],
        "series_tie": tied,
    }


def final_consensus_scope(game_id: str, aggregate: dict[str, Any],
                          sub_games: list[dict[str, Any]]) -> dict[str, Any]:
    """Return the negotiated symmetric scope, deliberately excluding ``tie``."""
    return {
        "game_id": game_id,
        "aggregate": aggregate,
        "sub_games": [
            {
                "sub_game_number": row["sub_game_number"],
                "roles": row["roles"],
                "result": row["result"],
                "winner_group": row["winner_group"],
                "score": row["score"],
            }
            for row in sub_games
        ],
    }


def build_declaration(game_id: str, game_uid: str, timezone: str, game_started_at: str,
                      game_ended_at: str, num_sub_games: int, max_tokens_per_game: int,
                      own: dict[str, Any], opponent: dict[str, Any]) -> dict[str, Any]:
    """Build and return declaration under the documented module contract."""
    return {"_schema": SCHEMA_DECLARATION, "schema_version": SCHEMA_VERSION,
            "declaration_type": "pre_game_declaration", "game_id": game_id,
            "game_uid": game_uid, "links": artifact_links(game_id), "timezone": timezone,
            "game_started_at": game_started_at, "game_ended_at": game_ended_at,
            "num_sub_games": num_sub_games, "max_tokens_per_game": max_tokens_per_game,
            "groups": {"group_1": _group(own), "group_2": _group(opponent)}}


def build_config_artifact(shared_terms: dict[str, Any], game_id: str, game_uid: str,
                          sub_game_number: int) -> dict[str, Any]:
    """Build and return config artifact under the documented module contract."""
    artifact = {"_schema": SCHEMA_CONFIG, **shared_terms}
    artifact.update({"schema_version": SCHEMA_VERSION, "game_id": game_id,
                     "game_uid": game_uid, "sub_game_number": sub_game_number,
                     "links": artifact_links(game_id),
                     "config_name": f"config_{game_id}_g{sub_game_number:02d}.json",
                     "config_sha256": canonical_sha256(shared_terms)})
    return artifact


def build_log(summary: dict[str, Any], game_id: str, game_uid: str, group_id: str,
              opponent_group_id: str) -> dict[str, Any]:
    """Build and return log under the documented module contract."""
    records = summary["records"]
    log_summary = {"sub_game_number": summary["sub_game_number"], "group_id": group_id,
                   "role": summary["role"], "opponent_group_id": opponent_group_id,
                   "result": summary["result"], "winner_role": summary["winner"],
                   "steps": summary["steps"],
                   "timezone": summary.get("timezone", DEFAULT_TIMEZONE),
                   "started_at": summary["started_at"],
                   "ended_at": _ended_at(summary["started_at"], summary["duration_seconds"]),
                   "duration_seconds": summary["duration_seconds"],
                   "tokens_total": summary["tokens_total"], "audit": summary["audit"]}
    return {"_schema": SCHEMA_LOG, "schema_version": SCHEMA_VERSION, "game_id": game_id,
            "game_uid": game_uid, "links": artifact_links(game_id), "summary": log_summary,
            "records": records, "mutual_agreement": {"opponent_group_id": opponent_group_id,
            "sha256": consensus_sha256(records), "confirmed": summary["audit"]["passed"]}}


def build_result(game_id: str, game_uid: str, group_ids: list[str] | tuple[str, ...],
                 sub_games: list[dict[str, Any]], aggregate_out: dict[str, Any],
                 mutual_sha256: str) -> dict[str, Any]:
    """Build and return result under the documented module contract."""
    final = {**aggregate_out,
             "tokens_total_series": {g: sum(s.get("tokens", {}).get(g, 0) for s in sub_games)
                                     for g in group_ids}}
    return {"_schema": SCHEMA_RESULT, "schema_version": SCHEMA_VERSION,
            "report_type": "final_game_result", "game_id": game_id, "game_uid": game_uid,
            "links": artifact_links(game_id), "timezone": DEFAULT_TIMEZONE,
            "groups": list(group_ids), "num_sub_games": len(sub_games), "sub_games": sub_games,
            "final_result": final, "mutual_agreement": {"sha256": mutual_sha256,
            "confirmed": all(s.get("audit", {}).get("log_verified", False) for s in sub_games)}}


def write_reference_v3_artifacts(directory: Path, game_id: str, game_uid: str,
        game_number: int, shared_terms: dict[str, Any], log_summary: dict[str, Any],
        own_identity: dict[str, Any], peer_identity: dict[str, Any], sub_game: dict[str, Any],
        aggregate_out: dict[str, Any], mutual_sha256: str, game_started_at: str,
        game_ended_at: str, max_tokens_per_game: int = 0) -> list[Path]:
    """Write deterministically reference v3 artifacts under the documented module contract."""
    values = {f"declaration_{game_id}.json": build_declaration(
        game_id, game_uid, DEFAULT_TIMEZONE, game_started_at, game_ended_at, 1,
        max_tokens_per_game, own_identity, peer_identity),
        f"config_{game_id}_g{game_number:02d}.json": build_config_artifact(
            shared_terms, game_id, game_uid, game_number),
        f"log_{game_id}_g{game_number:02d}.json": build_log(
            log_summary, game_id, game_uid, own_identity["group_id"], peer_identity["group_id"]),
        f"result_{game_id}.json": build_result(
            game_id, game_uid, sorted(
                [own_identity["group_id"], peer_identity["group_id"]]
            ),
            [sub_game], aggregate_out, mutual_sha256)}
    directory.mkdir(parents=True, exist_ok=True)
    paths = []
    for name, value in values.items():
        path = directory / name
        path.write_bytes(pretty_bytes(value))
        paths.append(path)
    return paths
