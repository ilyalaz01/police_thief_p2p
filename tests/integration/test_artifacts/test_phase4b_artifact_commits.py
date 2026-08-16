"""Phase 4B exact artifact commit-mapping check."""

import json
from pathlib import Path

from police_thief_lab.interop.artifacts import consensus_sha256, final_consensus_scope
from tests.support.interop_test_support import _run_reference_pair


def test_reference_artifacts_map_two_exact_group_commits(tmp_path: Path) -> None:
    exact = ("police/commit EXACT ", "thief-commit:@{opaque}")
    police, thief = _run_reference_pair(tmp_path, "capture", exact)
    expected = {"artifact-police": exact[0], "artifact-thief": exact[1]}
    for runtime_result in (police, thief):
        result_path = next(
            Path(path)
            for path in runtime_result["artifacts"]
            if Path(path).name.startswith("result_")
        )
        log_path = next(
            Path(path) for path in runtime_result["artifacts"] if Path(path).name.startswith("log_")
        )
        result = json.loads(result_path.read_text())
        log = json.loads(log_path.read_text())
        assert result["sub_games"][0]["github_commit"] == expected
        assert log["summary"]["group_id"] in expected
        assert log["summary"]["opponent_group_id"] in expected
        assert (
            consensus_sha256(
                final_consensus_scope(
                    result["game_id"],
                    {
                        key: result["final_result"][key]
                        for key in (
                            "total_score",
                            "sub_games_won",
                            "ties",
                            "winner_group",
                            "series_tie",
                        )
                    },
                    result["sub_games"],
                )
            )
            == result["mutual_agreement"]["sha256"]
        )
