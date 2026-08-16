"""Phase 4B end-to-end runtime artifact checks."""

import copy
import json
from pathlib import Path

import pytest
from interop_test_support import _reference_runtime_profile, _run_reference_pair

from police_thief_lab.interop.artifacts import (
    consensus_sha256,
    derive_game_ids,
    final_consensus_scope,
)


@pytest.mark.parametrize(
    ("outcome", "expected_score"),
    [
        ("capture", {"artifact-police": 20, "artifact-thief": 5}),
        ("survival", {"artifact-police": 5, "artifact-thief": 10}),
    ],
)
def test_reference_runtime_artifacts_score_uid_and_consensus_end_to_end(
    tmp_path: Path, outcome: str, expected_score: dict[str, int]
) -> None:
    police, thief = _run_reference_pair(tmp_path, outcome)
    results = []
    for _role, runtime_result in (("police", police), ("thief", thief)):
        docs = {}
        for raw_path in runtime_result["artifacts"]:
            path = Path(raw_path)
            docs[path.name.split("_", 1)[0]] = json.loads(path.read_text())
        assert set(docs) == {"declaration", "config", "log", "result"}
        assert all(doc["schema_version"] == "1.1" for doc in docs.values())
        result = docs["result"]
        assert result["groups"] == ["artifact-police", "artifact-thief"]
        row = result["sub_games"][0]
        assert row["score"] == expected_score
        assert result["final_result"]["total_score"] == expected_score
        assert row["github_commit"] == {
            "artifact-police": "UNRESOLVED_SELF_TEST_NO_GIT_METADATA",
            "artifact-thief": "UNRESOLVED_SELF_TEST_NO_GIT_METADATA",
        }
        assert row["log_files"] == {
            group: f"{group}/log_{result['game_id']}_g01.json" for group in expected_score
        }
        scope = final_consensus_scope(
            result["game_id"],
            {
                key: result["final_result"][key]
                for key in ("total_score", "sub_games_won", "ties", "winner_group", "series_tie")
            },
            result["sub_games"],
        )
        assert consensus_sha256(scope) == result["mutual_agreement"]["sha256"]
        results.append(result)
    assert {result["game_id"] for result in results} == {"artifact-police-vs-artifact-thief"}
    assert len({result["game_uid"] for result in results}) == 1
    assert len({result["mutual_agreement"]["sha256"] for result in results}) == 1
    expected_ids = derive_game_ids(
        _reference_runtime_profile(35).reference_terms(),
        "artifact-police",
        "artifact-thief",
    )
    assert (results[0]["game_id"], results[0]["game_uid"]) == expected_ids

    original = results[0]
    original_scope = final_consensus_scope(
        original["game_id"],
        {
            key: original["final_result"][key]
            for key in ("total_score", "sub_games_won", "ties", "winner_group", "series_tie")
        },
        original["sub_games"],
    )
    baseline = consensus_sha256(original_scope)
    noisy = copy.deepcopy(original)
    noisy["sub_games"][0].update(
        {"started_at": "changed", "tokens": {"x": 999}, "audit": {"log_verified": False}}
    )
    assert (
        consensus_sha256(
            final_consensus_scope(noisy["game_id"], original_scope["aggregate"], noisy["sub_games"])
        )
        == baseline
    )
    changed_result = "capture" if outcome == "survival" else "survival"
    for field, value in (
        ("result", changed_result),
        ("winner_group", "other"),
        ("score", {"artifact-police": 999, "artifact-thief": 0}),
    ):
        changed = copy.deepcopy(original["sub_games"])
        changed[0][field] = value
        assert (
            consensus_sha256(
                final_consensus_scope(original["game_id"], original_scope["aggregate"], changed)
            )
            != baseline
        )
