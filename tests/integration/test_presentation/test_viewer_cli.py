"""Replay Viewer command-line boundary tests."""

import json
from pathlib import Path

from police_thief_lab.interop.crypto import seal
from police_thief_lab.viewer_cli import main


def test_replay_cli_writes_standalone_verified_html(tmp_path: Path) -> None:
    config_path = tmp_path / "config.json"
    log_path = tmp_path / "log.json"
    output_path = tmp_path / "viewer" / "replay.html"
    config_path.write_text(
        json.dumps({"board_size": 7, "cop_start": [0, 0], "thief_start": [3, 3]}),
        encoding="utf-8",
    )
    log_path.write_text(
        json.dumps(
            {
                "game_id": "cli-game",
                "summary": {"role": "thief", "result": "survival"},
                "records": [
                    seal(
                        {
                            "step": 1,
                            "sender": "thief",
                            "position": [3, 4],
                            "action": {
                                "type": "move",
                                "direction": "E",
                                "barrier": None,
                            },
                        },
                        "cli-secret",
                    )
                ],
            }
        ),
        encoding="utf-8",
    )

    exit_code = main(
        [
            "replay",
            "--log",
            str(log_path),
            "--config",
            str(config_path),
            "--output",
            str(output_path),
        ]
    )

    assert exit_code == 0
    assert output_path.exists()
    html = output_path.read_text(encoding="utf-8")
    assert "cli-game" in html
    assert "Verified OK" in html
    assert "cli-secret" not in html
