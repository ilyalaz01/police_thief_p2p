"""Assembling one team's counted six-sub-game bundle from its own public results."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from police_thief_lab.league import assemble_public_series
from tests.support.league_fixtures import GROUP_A, GROUP_B, appendix_b_config

PROFILE = Path("interop/fixtures/phase4a5_reference_profile.json")
GAME_ID = f"{GROUP_A}-vs-{GROUP_B}"
SCHEDULE = {n: ({GROUP_A: "police", GROUP_B: "thief"} if n % 2 else
                {GROUP_A: "thief", GROUP_B: "police"}) for n in range(1, 7)}
SCORES = {"capture": {"police": 20, "thief": 5}, "survival": {"police": 5, "thief": 10}}


def _declaration(group_id: str, name: str) -> dict:
    """Return one complete operator declaration document."""
    return {
        "group_id": group_id, "group_name": name, "members": [f"{name} One"],
        "cop_repo": f"https://github.com/example/{name}-cop",
        "thief_repo": f"https://github.com/example/{name}-thief",
        "cop_mcp_url": f"https://{name}-cop.example/mcp",
        "thief_mcp_url": f"https://{name}-thief.example/mcp",
        "llm_model": "deterministic-python",
        "hardware": {"cpu_type": "CPU", "cpu_freq_mhz": 2500, "cpu_cores": 8,
                     "ram_gb": 16, "gpu_model": "none", "vram_gb": 0},
    }


def _sub_game(tmp_path: Path, number: int, outcome: str, config_sha: str) -> Path:
    """Write one verified peer result with its four schema-1.1 artifacts."""
    roles = SCHEDULE[number]
    score = {group: SCORES[outcome][role] for group, role in roles.items()}
    winner = next(g for g, r in roles.items()
                  if r == ("police" if outcome == "capture" else "thief"))
    directory = tmp_path / f"g{number:02d}"
    directory.mkdir(parents=True, exist_ok=True)
    row = {
        "sub_game_number": 1, "roles": roles,
        "started_at": f"2026-08-22T10:0{number}:00+00:00",
        "ended_at": f"2026-08-22T10:0{number}:30+00:00",
        "result": outcome, "winner_group": winner,
        "github_commit": {GROUP_A: "a" * 40, GROUP_B: "b" * 40},
        "tokens": {GROUP_A: 0, GROUP_B: 0}, "score": score,
        "log_files": {}, "audit": {"log_verified": True, "tampered": False},
    }
    documents = {
        f"declaration_{GAME_ID}.json": {"schema_version": "1.1"},
        f"config_{GAME_ID}_g01.json": {"schema_version": "1.1"},
        f"log_{GAME_ID}_g01.json": {
            "schema_version": "1.1",
            "summary": {"group_id": GROUP_A, "role": roles[GROUP_A], "result": outcome,
                        "winner_role": "police" if outcome == "capture" else "thief",
                        "steps": 12, "timezone": "Asia/Jerusalem",
                        "started_at": row["started_at"], "ended_at": row["ended_at"],
                        "duration_seconds": 30.0, "tokens_total": 0,
                        "audit": {"passed": True, "verified_steps": 12, "failed_steps": []}},
            "records": [{"payload": {"step": 1}, "nonce": "n", "commit": "c" * 64}],
        },
        f"result_{GAME_ID}.json": {
            "schema_version": "1.1", "game_id": GAME_ID, "sub_games": [row],
            "final_result": {"total_score": score, "sub_games_won": {}, "ties": 0,
                             "winner_group": winner, "series_tie": False},
            "mutual_agreement": {"sha256": f"{number:064d}", "confirmed": True},
        },
    }
    paths = []
    for name, value in documents.items():
        path = directory / name
        path.write_text(json.dumps(value, ensure_ascii=False), encoding="utf-8")
        paths.append(str(path))
    result = {"ok": True, "phase": "verified", "config_sha256": config_sha,
              "records": 20, "audit": {"verified": True}, "replay": {"verified": True},
              "artifacts": paths}
    output = directory / "peer-result.json"
    output.write_text(json.dumps(result, ensure_ascii=False), encoding="utf-8")
    return output


def _inputs(tmp_path: Path, outcomes: list[str]) -> dict:
    """Prepare declarations, the agreed configuration and six sub-game results."""
    import police_thief_lab.interop.profile as profile_module

    raw = json.loads(PROFILE.read_text(encoding="utf-8"))
    config_sha = profile_module.MatchProfile(**raw).sha256
    ours = tmp_path / "ours.json"
    ours.write_text(json.dumps(_declaration(GROUP_A, "alpha")), encoding="utf-8")
    theirs = tmp_path / "theirs.json"
    theirs.write_text(json.dumps(_declaration(GROUP_B, "bravo")), encoding="utf-8")
    shared = tmp_path / "game.json"
    shared.write_text(json.dumps(appendix_b_config()), encoding="utf-8")
    results = tuple(
        _sub_game(tmp_path, number, outcome, config_sha)
        for number, outcome in enumerate(outcomes, start=1)
    )
    return {"our_declaration": ours, "peer_declaration": theirs, "appendix_b": shared,
            "profile": PROFILE, "results": results, "out": tmp_path / "bundle"}


def test_six_verified_sub_games_produce_one_bundle(tmp_path: Path) -> None:
    summary = assemble_public_series(**_inputs(tmp_path, ["capture"] * 6))
    assert summary["game_id"] == GAME_ID
    assert summary["aggregate"]["total_score"] == {GROUP_A: 75, GROUP_B: 75}
    assert summary["aggregate"]["series_tie"] is True
    assert summary["aggregate"]["series_tie_score"] == {GROUP_A: 2, GROUP_B: 2}
    assert summary["mailed"] is False
    assert len(summary["sub_game_consensus_sha256"]) == 6
    bundle = tmp_path / "bundle" / "artifacts"
    assert (bundle / f"result_{GAME_ID}.json").is_file()
    assert len(list(bundle.glob(f"config_{GAME_ID}_g*.json"))) == 6
    assert len(list(bundle.glob(f"log_{GAME_ID}_g*.json"))) == 6
    result = json.loads((bundle / f"result_{GAME_ID}.json").read_text(encoding="utf-8"))
    assert result["num_sub_games"] == 6
    assert result["mutual_agreement"]["sha256"] == summary["series_consensus_sha256"]


def test_a_decided_series_reports_its_winner(tmp_path: Path) -> None:
    outcomes = ["capture", "survival", "capture", "survival", "capture", "survival"]
    summary = assemble_public_series(**_inputs(tmp_path, outcomes))
    assert summary["aggregate"]["series_tie"] is False
    assert summary["aggregate"]["winner_group"] == GROUP_A
    assert summary["aggregate"]["series_tie_score"] is None


def test_an_unverified_sub_game_stops_the_assembly(tmp_path: Path) -> None:
    inputs = _inputs(tmp_path, ["capture"] * 6)
    broken = Path(inputs["results"][3])
    value = json.loads(broken.read_text(encoding="utf-8"))
    value["replay"] = {"verified": False}
    broken.write_text(json.dumps(value), encoding="utf-8")
    with pytest.raises(ValueError, match="sub-game 4 is not a verified peer result"):
        assemble_public_series(**inputs)


def test_fewer_than_six_results_are_refused(tmp_path: Path) -> None:
    inputs = _inputs(tmp_path, ["capture"] * 6)
    inputs["results"] = inputs["results"][:5]
    with pytest.raises(ValueError):
        assemble_public_series(**inputs)
