"""Assemble two symmetric role bundles from verified localhost evidence."""

from __future__ import annotations

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
)
from ..interop.profile import MatchProfile
from .config import AppendixBConfigLock
from .identity import TeamDeclarationIdentity
from .series import series_reference_terms

_AGGREGATE_FIELDS = ("total_score", "sub_games_won", "ties", "winner_group", "series_tie")


def _write(path: Path, value: dict[str, Any] | bytes) -> Path:
    """Write one new artifact path, refusing any accidental overwrite."""
    if path.exists():
        raise ValueError("series artifact path already exists")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(value if isinstance(value, bytes) else pretty_bytes(value))
    return path


def write_series_bundle(
    root: Path,
    game_id: str,
    game_uid: str,
    profile: MatchProfile,
    lock: AppendixBConfigLock,
    identities: dict[str, TeamDeclarationIdentity],
    rows: tuple[dict[str, Any], ...],
    aggregate: dict[str, Any],
    logs: dict[int, dict[str, dict[str, Any]]],
    peer_checks: tuple[dict[str, Any], ...],
    max_tokens_per_game: int,
) -> tuple[tuple[Path, ...], Path, str]:
    """Write both complete local bundles and return paths plus mutual result hash."""
    groups = tuple(sorted(identities))
    artifact_aggregate = {field: aggregate[field] for field in _AGGREGATE_FIELDS}
    mutual_sha = consensus_sha256(final_consensus_scope(game_id, artifact_aggregate, list(rows)))
    result = build_result(game_id, game_uid, groups, list(rows), artifact_aggregate, mutual_sha)
    declaration_times = (rows[0]["started_at"], rows[-1]["ended_at"])
    paths: list[Path] = []
    for group in groups:
        peer = next(other for other in groups if other != group)
        directory = root / group
        paths.append(_write(directory / "config/game.json", lock.bytes))
        paths.append(
            _write(
                directory / f"declaration_{game_id}.json",
                build_declaration(
                    game_id,
                    game_uid,
                    "Asia/Jerusalem",
                    *declaration_times,
                    6,
                    max_tokens_per_game,
                    identities[group].object(),
                    identities[peer].object(),
                ),
            )
        )
        for number in range(1, 7):
            paths.append(
                _write(
                    directory / f"config_{game_id}_g{number:02d}.json",
                    build_config_artifact(
                        series_reference_terms(profile), game_id, game_uid, number
                    ),
                )
            )
            paths.append(
                _write(
                    directory / f"log_{game_id}_g{number:02d}.json",
                    build_log(logs[number][group], game_id, game_uid, group, peer),
                )
            )
        paths.append(_write(directory / f"result_{game_id}.json", result))
    evidence = {
        "classification": "UNCOUNTED_LOCALHOST_SELF_TEST",
        "status": "GREEN_LOCALHOST_ONLY",
        "sub_games": 6,
        "peer_results_verified": len(peer_checks),
        "appendix_b_scope": lock.scope,
        "appendix_b_sha256": lock.sha256,
        "runtime_profile_sha256": profile.sha256,
        "mutual_result_sha256": mutual_sha,
        "aggregate": aggregate,
        "public_transport_claimed": False,
        "bilateral_real_team_approval_claimed": False,
        "counted_operation_claimed": False,
        "live_nonces_retained_in_evidence": False,
    }
    evidence_path = _write(root / "series_evidence.json", evidence)
    return tuple(paths), evidence_path, mutual_sha
