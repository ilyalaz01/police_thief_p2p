"""Phase 4B pinned artifact-builder and result-row checks."""

import copy
import json
import os
import subprocess
import sys

import pytest

from police_thief_lab.interop.artifacts import (
    build_config_artifact,
    build_declaration,
    build_log,
    build_result,
)
from tests.support.project_paths import PROJECT_ROOT


def _identity(group: str, url: str) -> dict:
    return {
        "group_id": group,
        "group_name": group.title(),
        "members": ["id-1"],
        "repos": {"cop": "repo-c", "thief": "repo-t"},
        "mcp_servers": {"cop": url},
        "llm_model": "deterministic-python",
        "spec": {
            "cpu_type": "cpu",
            "cpu_freq_mhz": 1,
            "cpu_cores": 2,
            "ram_gb": 3,
            "gpu_type": None,
            "vram_gb": 0,
        },
    }


def _artifact_inputs() -> dict:
    records = [{"payload": {"step": 1}, "nonce": "n", "commit": "c"}]
    summary = {
        "records": records,
        "sub_game_number": 1,
        "role": "cop",
        "result": "capture",
        "winner": "cop",
        "steps": 1,
        "started_at": "2026-08-15T00:00:00+00:00",
        "duration_seconds": 2.5,
        "tokens_total": 0,
        "audit": {"passed": True, "verified_steps": 1, "failed_steps": []},
    }
    sub = {
        "sub_game_number": 1,
        "roles": {"alpha": "cop", "beta": "thief"},
        "result": "capture",
        "winner_group": "alpha",
        "tokens": {},
        "audit": {"log_verified": True},
    }
    aggregate = {
        "total_score": {},
        "sub_games_won": {"alpha": 1, "beta": 0},
        "ties": 0,
        "winner_group": "alpha",
        "series_tie": False,
    }
    return {
        "terms": {"board_size": 7, "setting": "ירושלים🙂"},
        "summary": summary,
        "sub": sub,
        "aggregate": aggregate,
    }


def test_all_four_artifacts_exactly_match_pinned_professor_builders() -> None:
    professor_src = PROJECT_ROOT / "external/Game-P2P-Cop-Chase/src"
    if not professor_src.exists():
        pytest.skip("professor-owned reference implementation is not redistributed")
    data = _artifact_inputs()
    own, peer = (
        _identity("alpha", "https://alpha.example/mcp"),
        _identity("beta", "https://beta.example/mcp"),
    )
    ours = [
        build_declaration("game", "uid", "Asia/Jerusalem", "start", "end", 1, 0, own, peer),
        build_config_artifact(data["terms"], "game", "uid", 1),
        build_log(data["summary"], "game", "uid", "alpha", "beta"),
        build_result(
            "game", "uid", ["alpha", "beta"], [data["sub"]], data["aggregate"], "agreed-hash"
        ),
    ]
    script = """
import json,sys
from police_thief.report.artifacts import (
    build_config_artifact, build_declaration, build_log, build_result
)
d=json.load(sys.stdin); own=d['own']; peer=d['peer']; x=d['data']
print(json.dumps([build_declaration('game','uid','Asia/Jerusalem','start','end',1,0,own,peer),build_config_artifact(x['terms'],'game','uid',1),build_log(x['summary'],'game','uid','alpha','beta'),build_result('game','uid',['alpha','beta'],[x['sub']],x['aggregate'],'agreed-hash')],ensure_ascii=False))
"""
    env = os.environ | {"PYTHONPATH": str(professor_src)}
    encoded = json.dumps({"own": own, "peer": peer, "data": data}).encode()
    raw = subprocess.check_output([sys.executable, "-c", script], input=encoded, env=env)
    assert ours == json.loads(raw)


@pytest.mark.parametrize("with_tie", [False, True])
def test_result_rows_are_never_silently_modified(with_tie: bool) -> None:
    data = _artifact_inputs()
    row = copy.deepcopy(data["sub"])
    if with_tie:
        row["tie"] = False
    result = build_result("game", "uid", ["alpha", "beta"], [row], data["aggregate"], "hash")
    assert result["sub_games"][0] == row
    assert ("tie" in result["sub_games"][0]) is with_tie
