"""Shared schema 1.1 artifact characterization inputs."""

import hashlib

from police_thief_lab.interop.artifacts import (
    build_config_artifact,
    build_declaration,
    build_log,
    build_result,
)


def _inputs() -> tuple[dict, ...]:
    own = {
        "group_id": "alpha",
        "group_name": "Alpha",
        "members": ["id-1"],
        "repos": {"cop": "repo-c", "thief": "repo-t"},
        "mcp_servers": {"cop": "https://alpha.example/mcp"},
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
    peer = own | {
        "group_id": "beta",
        "group_name": "Beta",
        "mcp_servers": {"cop": "https://beta.example/mcp"},
    }
    terms = {"board_size": 7, "setting": "ירושלים🙂"}
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
        "score": {"alpha": 20, "beta": 5},
        "tie": True,
        "tokens": {"alpha": 3},
        "audit": {"log_verified": True},
        "started_at": "excluded",
        "github_commit": {"alpha": "x"},
    }
    aggregate = {
        "total_score": {"alpha": 20, "beta": 5},
        "sub_games_won": {"alpha": 1, "beta": 0},
        "ties": 0,
        "winner_group": "alpha",
        "series_tie": False,
    }
    return own, peer, terms, records, summary, sub, aggregate


def _objects() -> list[dict]:
    own, peer, terms, _records, summary, sub, aggregate = _inputs()
    return [
        build_declaration("game", "uid", "Asia/Jerusalem", "start", "end", 1, 0, own, peer),
        build_config_artifact(terms, "game", "uid", 1),
        build_log(summary, "game", "uid", "alpha", "beta"),
        build_result("game", "uid", ["alpha", "beta"], [sub], aggregate, "agreed-hash"),
    ]


def _sha(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()
