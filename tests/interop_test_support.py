"""Neutral helpers shared by interoperability test modules."""

import socket
from pathlib import Path

from police_thief_lab.interop.profile import MatchProfile

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
