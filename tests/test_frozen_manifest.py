"""Regression evidence for the authoritative seven frozen production files."""

from __future__ import annotations

import hashlib
from pathlib import Path

ROOT = Path(__file__).parents[1]
AUTHORITATIVE_FROZEN_SHA256 = {
    "src/police_thief_lab/models.py":
        "ab0714497d6720d1d06eede6a7b9ea52ebb5b559bddece17de1caecfd6898410",
    "src/police_thief_lab/rules.py":
        "90fd388cf1a4ea318f305b8eb5c692c9d05bdffeca43cad81cb381c6f48657ab",
    "src/police_thief_lab/scent.py":
        "27b1b395402b6b072e1b4d78e9e081cbf11806d5f5c4a3c00b1a4c4508faec99",
    "src/police_thief_lab/turns.py":
        "38be6e861a2433b81db92f7a9a6f9d422a7c123e159a908110438a07b6a1aca9",
    "src/police_thief_lab/simulator.py":
        "0d9faab437f78e123e1fb4bab178a951866d10d5bd01ccf5df8a67a080f53110",
    "src/police_thief_lab/policies/tactical.py":
        "4b158025cf05edb975da1e2cd5b3e0a9b9ac44b42f018e7b8138a4f29b1d4dfb",
    "src/police_thief_lab/interop/crypto.py":
        "6ce9d1c0ea3185c60583d4f4cc0512aadf7a22f2194162a45fb33cfdeaa9294e",
}


def test_authoritative_seven_frozen_file_hashes() -> None:
    expected_paths = {
        "src/police_thief_lab/models.py",
        "src/police_thief_lab/rules.py",
        "src/police_thief_lab/scent.py",
        "src/police_thief_lab/turns.py",
        "src/police_thief_lab/simulator.py",
        "src/police_thief_lab/policies/tactical.py",
        "src/police_thief_lab/interop/crypto.py",
    }
    assert set(AUTHORITATIVE_FROZEN_SHA256) == expected_paths
    assert len(AUTHORITATIVE_FROZEN_SHA256) == 7
    actual = {
        path: hashlib.sha256((ROOT / path).read_bytes()).hexdigest()
        for path in AUTHORITATIVE_FROZEN_SHA256
    }
    assert actual == AUTHORITATIVE_FROZEN_SHA256
