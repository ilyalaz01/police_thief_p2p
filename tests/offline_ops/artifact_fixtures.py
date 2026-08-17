"""Synthetic, minimal, MIT-checker-valid match artifact fixtures for tests.

Shaped after the composed checker's own selftest fixture in
``external/copthief-league-protocol/tools/check_artifacts.py`` (a clean,
single-sub-game set), but built independently here from literal values —
never by importing or calling that checker's code.
"""

from __future__ import annotations

import json
from pathlib import Path

GROUP_A = "alpha"
GROUP_B = "bravo"
GAME_ID = "alpha-vs-bravo"
GAME_UID = "11111111-1111-4111-8111-111111111111"


def write_valid_match_fixture(directory: Path) -> None:
    """Write one clean, single-sub-game, four-family artifact set."""
    directory.mkdir(parents=True, exist_ok=True)
    base = {"game_id": GAME_ID, "game_uid": GAME_UID}
    files = {
        f"declaration_{GAME_ID}.json": {
            **base,
            "num_sub_games": 1,
            "groups": {"group_1": {"group_id": GROUP_A}, "group_2": {"group_id": GROUP_B}},
        },
        f"config_{GAME_ID}_g01.json": {**base, "sub_game_number": 1},
        f"log_{GAME_ID}_g01.json": {
            **base,
            "summary": {"sub_game_number": 1},
            "records": [],
        },
        f"result_{GAME_ID}.json": {
            **base,
            "num_sub_games": 1,
            "groups": [{"group_id": GROUP_A}, {"group_id": GROUP_B}],
            "sub_games": [{"sub_game_number": 1, "score": {GROUP_A: 20, GROUP_B: 5}}],
            "final_result": {"total_score": {GROUP_A: 20, GROUP_B: 5}},
        },
    }
    for name, doc in files.items():
        (directory / name).write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")
