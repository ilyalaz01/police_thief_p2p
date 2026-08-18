"""End-to-end proof for six real localhost peer games and final artifacts."""

import json
from pathlib import Path

from police_thief_lab import PoliceThiefSDK
from police_thief_lab.league import LocalhostSeriesRequest


def _load(path: Path) -> dict:
    """Read one generated JSON artifact."""
    return json.loads(path.read_text(encoding="utf-8"))


def test_six_localhost_games_produce_verified_symmetric_series_bundle(
    localhost_series_request: LocalhostSeriesRequest,
) -> None:
    result = PoliceThiefSDK().league.run_localhost_series(localhost_series_request)
    root = localhost_series_request.output_dir
    groups = tuple(sorted(identity.group_id for identity in localhost_series_request.identities))

    assert [row["sub_game_number"] for row in result.rows] == list(range(1, 7))
    assert len(result.peer_checks) == 12
    assert all(check["audit_verified"] and check["replay_verified"] for check in result.peer_checks)
    assert all(row["audit"] == {"log_verified": True, "tampered": False} for row in result.rows)
    assert result.aggregate["total_score"] == {
        group: sum(row["score"][group] for row in result.rows) for group in groups
    }

    full_configs = [(root / group / "config/game.json").read_bytes() for group in groups]
    assert full_configs == [localhost_series_request.config_lock.bytes] * 2
    for number in range(1, 7):
        names = [
            root / group / "artifacts" / f"config_{result.game_id}_g{number:02d}.json"
            for group in groups
        ]
        assert names[0].read_bytes() == names[1].read_bytes()
        for group in groups:
            log = _load(
                root / group / "artifacts" / f"log_{result.game_id}_g{number:02d}.json"
            )
            assert log["summary"]["sub_game_number"] == number
            assert log["summary"]["audit"]["passed"] is True

    result_paths = [
        root / group / "artifacts" / f"result_{result.game_id}.json" for group in groups
    ]
    assert result_paths[0].read_bytes() == result_paths[1].read_bytes()
    final = _load(result_paths[0])
    assert final["num_sub_games"] == 6
    assert final["mutual_agreement"]["confirmed"] is True
    assert final["mutual_agreement"]["sha256"] == result.mutual_sha256
    assert not (root / "_raw").exists()


def test_failed_peer_prevents_any_final_bundle(
    localhost_series_request: LocalhostSeriesRequest,
    monkeypatch,
) -> None:
    from police_thief_lab.league import local_series

    monkeypatch.setattr(
        local_series,
        "run_localhost_pair",
        lambda *_args, **_kwargs: {
            slot_group: {"ok": False, "phase": "failed", "error": "synthetic"}
            for slot_group in ("alpha001", "bravo002")
        },
    )
    try:
        PoliceThiefSDK().league.run_localhost_series(localhost_series_request)
    except ValueError as exc:
        assert "verified peer result" in str(exc)
    else:
        raise AssertionError("failed peer pair was accepted")
    assert not localhost_series_request.output_dir.exists()
