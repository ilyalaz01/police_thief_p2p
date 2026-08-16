"""Neutral helpers shared by interoperability test modules."""

import socket
import threading
from pathlib import Path

from police_thief_lab.interop.profile import MatchProfile
from police_thief_lab.interop.runtime import PeerRuntime
from police_thief_lab.models import Direction, MoveType, Role

ROOT = Path(__file__).parents[1]


def frame(step: int, commit: str = "a" * 64, hint: str = "שלום 🙂") -> dict:
    return {
        "step": step,
        "sender": "thief",
        "hint": hint,
        "smell_grid": {"1,2": 0.8},
        "commit": commit,
        "timestamp": "2026-08-15T00:00:01+03:00",
        "barrier_placed": None,
        "capture_claim": None,
        "claim_response": None,
        "win_claim": None,
        "extension": "tolerated",
    }


def profile() -> MatchProfile:
    return MatchProfile(
        {
            "board_size": 7,
            "police_start": [0, 0],
            "thief_start": [3, 3],
            "blocked_cells": [],
            "barrier_quota": 14,
        }
    )


def free_port() -> int:
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


class _FixedPolicy:
    def __init__(self, direction: Direction | None) -> None:
        self.direction = direction

    def choose_action(self, observation):
        for action in observation.legal_actions:
            if self.direction is None and action.move_type is MoveType.STAY:
                return action
            if action.move_type is MoveType.MOVE and action.direction is self.direction:
                return action
        raise AssertionError("fixed test action unavailable")


def _reference_runtime_profile(survival_limit: int) -> MatchProfile:
    return MatchProfile(
        {
            "board_size": 7,
            "police_start": [0, 0],
            "thief_start": [0, 1],
            "blocked_cells": [],
            "barrier_quota": 14,
        },
        survival_limit=survival_limit,
        move_limit=35,
        timeouts={"connect": 5.0, "turn": 5.0, "audit": 5.0, "retry": 0.01, "retry_count": 100},
        artifact_profile="reference-v3-artifact-1.1",
        artifact_schema="1.1",
        consensus_scope="reference_symmetric_outcome_without_tie",
        setting="New York",
        minimum_center_intensity=0.5,
        step_numbering="sender_local",
    )


def _run_reference_pair(
    tmp_path: Path, outcome: str, commits: tuple[str | None, str | None] = (None, None)
) -> tuple[dict, dict]:
    police_port, thief_port = free_port(), free_port()
    shared = _reference_runtime_profile(35)
    police = PeerRuntime(
        Role.POLICE,
        shared,
        "127.0.0.1",
        police_port,
        f"http://127.0.0.1:{thief_port}/mcp",
        tmp_path / "police",
        group_id="artifact-police",
        group_name="Artifact Police",
        git_commit=commits[0],
    )
    thief = PeerRuntime(
        Role.THIEF,
        shared,
        "127.0.0.1",
        thief_port,
        f"http://127.0.0.1:{police_port}/mcp",
        tmp_path / "thief",
        group_id="artifact-thief",
        group_name="Artifact Thief",
        git_commit=commits[1],
    )
    police.backend = _FixedPolicy(Direction.E)
    thief.backend = _FixedPolicy(None)
    if outcome == "survival":
        thief.state.own_moves = 34
    results: dict[str, dict] = {}
    threads = [
        threading.Thread(target=lambda: results.setdefault("police", police.run())),
        threading.Thread(target=lambda: results.setdefault("thief", thief.run())),
    ]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(15)
    assert not any(thread.is_alive() for thread in threads)
    assert results["police"]["ok"] and results["thief"]["ok"]
    return results["police"], results["thief"]
