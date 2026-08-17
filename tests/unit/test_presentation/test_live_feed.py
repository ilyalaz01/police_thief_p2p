"""Sanitized bounded Live GUI feed contracts."""

import json
from pathlib import Path

import pytest

from police_thief_lab import GameConfig, Position, Role, Simulator
from police_thief_lab.presentation import TurnBanner, build_live_view
from police_thief_lab.presentation.live_feed import LiveViewPublisher, load_live_feed


def _view(banner: TurnBanner, step: int = 0):
    observation = Simulator(GameConfig()).observe(Role.THIEF)
    return build_live_view(
        observation,
        {Position(0, 0): 0.75, Position(0, 1): 0.25},
        banner,
        step,
    )


def test_publisher_retains_bounded_role_safe_history_atomically(tmp_path: Path) -> None:
    path = tmp_path / "nested" / "live.json"
    publisher = LiveViewPublisher(path, history_limit=2)

    publisher.publish(_view(TurnBanner.LOCKED, 0))
    publisher.publish(_view(TurnBanner.YOUR_TURN, 1))
    publisher.publish(_view(TurnBanner.GAME_OVER, 2))

    feed = load_live_feed(path)
    assert feed["schema_version"] == "1.0"
    assert [item["revision"] for item in feed["updates"]] == [2, 3]
    assert [item["view"]["banner"] for item in feed["updates"]] == [
        "YOUR TURN",
        "GAME OVER",
    ]
    raw = path.read_text(encoding="utf-8")
    assert "opponent_position" not in raw
    assert "nonce" not in raw and "commit" not in raw
    assert not path.with_suffix(path.suffix + ".tmp").exists()


def test_loader_rejects_unapproved_root_or_view_fields(tmp_path: Path) -> None:
    path = tmp_path / "live.json"
    publisher = LiveViewPublisher(path)
    publisher.publish(_view(TurnBanner.LOCKED))
    payload = json.loads(path.read_text(encoding="utf-8"))

    payload["secret"] = "must-not-pass"
    path.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(ValueError, match="feed fields"):
        load_live_feed(path)

    del payload["secret"]
    payload["updates"][0]["view"]["opponent_position"] = [6, 6]
    path.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(ValueError, match="view fields"):
        load_live_feed(path)

