"""Coordinate six localhost games and publish an atomic verified series bundle."""

from __future__ import annotations

import tempfile
from pathlib import Path
from typing import Any

from .local_bundle import write_series_bundle
from .local_evidence import extract_pair_evidence
from .local_models import LocalhostSeriesRequest, LocalhostSeriesResult
from .local_runtime import run_localhost_pair
from .local_validation import validate_localhost_request
from .series import (
    aggregate_series_rows,
    coordinate_offline_series,
    derive_series_game_ids,
    series_token_totals,
)


def _publish(
    request: LocalhostSeriesRequest,
    game_id: str,
    game_uid: str,
    identities: dict,
    rows: tuple[dict[str, Any], ...],
    aggregate: dict[str, Any],
    logs: dict[int, dict[str, dict[str, Any]]],
    checks: tuple[dict[str, Any], ...],
) -> tuple[tuple[Path, ...], Path, str]:
    """Stage the complete output and rename it only after every write succeeds."""
    parent = request.output_dir.parent
    parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="police-thief-series-stage-", dir=parent) as raw:
        staging = Path(raw) / "bundle"
        paths, evidence, mutual = write_series_bundle(
            staging,
            game_id,
            game_uid,
            request.profile,
            request.config_lock,
            identities,
            rows,
            aggregate,
            logs,
            checks,
            request.max_tokens_per_game,
        )
        staging.replace(request.output_dir)
    rebased = tuple(request.output_dir / path.relative_to(staging) for path in paths)
    return rebased, request.output_dir / evidence.relative_to(staging), mutual


def run_localhost_series(request: LocalhostSeriesRequest) -> LocalhostSeriesResult:
    """Run six real loopback games, verify both peers, and publish one final bundle."""
    identities, commits, watchdog = validate_localhost_request(request)
    groups = tuple(sorted(identities))
    game_id, game_uid = derive_series_game_ids(request.profile, *groups)
    logs: dict[int, dict[str, dict[str, Any]]] = {}
    checks: list[dict[str, Any]] = []
    with tempfile.TemporaryDirectory(prefix="police-thief-series-raw-") as raw:
        raw_root = Path(raw)

        def runner(slot) -> dict[str, Any]:
            """Run and validate one sealed slot for the existing coordinator."""
            results = run_localhost_pair(
                slot,
                request.profile,
                identities,
                commits[slot.sub_game_number],
                raw_root / f"g{slot.sub_game_number:02d}",
                request.seed + slot.sub_game_number - 1,
                watchdog,
            )
            row, slot_logs, slot_checks = extract_pair_evidence(
                slot,
                results,
                request.profile,
                commits[slot.sub_game_number],
                game_id,
            )
            logs[slot.sub_game_number] = slot_logs
            checks.extend(slot_checks)
            return row

        rows = coordinate_offline_series(request.schedule, runner)
        aggregate = aggregate_series_rows(rows, groups)
        token_totals = series_token_totals(rows, groups)
        if token_totals != dict.fromkeys(groups, 0):
            raise ValueError("localhost deterministic peers unexpectedly reported tokens")
        paths, evidence, mutual = _publish(
            request,
            game_id,
            game_uid,
            identities,
            rows,
            aggregate,
            logs,
            tuple(checks),
        )
    return LocalhostSeriesResult(
        game_id,
        game_uid,
        rows,
        aggregate,
        mutual,
        tuple(checks),
        paths,
        evidence,
    )
