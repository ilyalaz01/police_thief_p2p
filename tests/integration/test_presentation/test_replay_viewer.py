"""Artifact-backed Replay Viewer acceptance tests."""

import copy

from police_thief_lab.interop.crypto import seal
from police_thief_lab.presentation import build_replay, render_replay_html


def _config() -> dict:
    return {
        "board_size": 7,
        "cop_start": [0, 0],
        "thief_start": [3, 3],
    }


def _log() -> dict:
    records = [
        seal(
            {
                "step": 1,
                "sender": "thief",
                "position": [3, 4],
                "action": {"type": "move", "direction": "E", "barrier": None},
            },
            "thief-secret",
        ),
        seal(
            {
                "step": 2,
                "sender": "police",
                "position": [1, 0],
                "action": {"type": "move", "direction": "S", "barrier": None},
            },
            "police-secret",
        ),
    ]
    return {
        "game_id": "demo-game",
        "summary": {"role": "police", "result": "capture"},
        "records": records,
    }


def test_verified_replay_builds_two_agent_frames_and_safe_html() -> None:
    replay = build_replay(_log(), _config())
    html = render_replay_html(replay)

    assert replay.verdict == "Verified OK"
    assert replay.failed_commit_indices == ()
    assert replay.frames[0].police_position == (0, 0)
    assert replay.frames[0].thief_position == (3, 3)
    assert replay.frames[-1].police_position == (1, 0)
    assert replay.frames[-1].thief_position == (3, 4)
    assert "Verified OK" in html
    assert "Previous step" in html and "Next step" in html
    assert "thief-secret" not in html and "police-secret" not in html


def test_legacy_runtime_profile_board_config_is_supported() -> None:
    replay = build_replay(_log(), {"board_config": _config()})

    assert replay.verdict == "Verified OK"
    assert replay.board_size == 7


def test_one_changed_reveal_marks_whole_replay_tampered() -> None:
    tampered = copy.deepcopy(_log())
    tampered["records"][1]["payload"]["position"] = [2, 0]

    replay = build_replay(tampered, _config())
    html = render_replay_html(replay)

    assert replay.verdict == "TAMPERED"
    assert replay.failed_commit_indices == (1,)
    assert "TAMPERED" in html
    assert "data-verdict=\"tampered\"" in html


def test_physics_failure_is_tampered_even_with_valid_commit() -> None:
    invalid = _log()
    invalid["records"][1] = seal(
        {
            "step": 2,
            "sender": "police",
            "position": [6, 6],
            "action": {"type": "move", "direction": "S", "barrier": None},
        },
        "valid-but-impossible",
    )

    replay = build_replay(invalid, _config())

    assert replay.verdict == "TAMPERED"
    assert replay.physics_errors
