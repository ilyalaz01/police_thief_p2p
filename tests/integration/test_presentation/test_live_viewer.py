"""Local-only Live GUI HTTP and HTML acceptance tests."""

import json
import threading
import urllib.request
from pathlib import Path

import pytest

from police_thief_lab import GameConfig, Position, Role, Simulator
from police_thief_lab.presentation import TurnBanner, build_live_view, render_live_html
from police_thief_lab.presentation.live_feed import LiveViewPublisher
from police_thief_lab.presentation.live_server import build_live_server
from tests.support.project_paths import PROJECT_ROOT


def _snapshot(path: Path) -> None:
    observation = Simulator(GameConfig()).observe(Role.POLICE)
    view = build_live_view(
        observation,
        {Position(3, 3): 0.8, Position(3, 4): 0.2},
        TurnBanner.YOUR_TURN,
        1,
    )
    LiveViewPublisher(path).publish(view)


def test_live_html_has_heatmap_status_history_and_no_hidden_truth() -> None:
    html = render_live_html()

    assert "Live GUI (Local Truth)" in html
    assert "YOUR TURN" in html and "LOCKED" in html
    assert "Previous snapshot" in html and "Next snapshot" in html
    assert "snapshot.json" in html
    assert "aria-live" in html
    assert "opponent_position" not in html


def test_loopback_server_serves_sanitized_feed_and_security_headers(tmp_path: Path) -> None:
    snapshot = tmp_path / "live.json"
    _snapshot(snapshot)
    server = build_live_server(snapshot, "127.0.0.1", 0)
    thread = threading.Thread(target=server.serve_forever)
    thread.start()
    try:
        root = urllib.request.urlopen(  # noqa: S310 - fixed loopback test server
            f"http://127.0.0.1:{server.server_port}/", timeout=2
        )
        feed = urllib.request.urlopen(  # noqa: S310 - fixed loopback test server
            f"http://127.0.0.1:{server.server_port}/snapshot.json", timeout=2
        )
        payload = json.loads(feed.read())
        assert root.status == 200 and b"Live GUI" in root.read()
        assert root.headers["Content-Security-Policy"]
        assert root.headers["Cache-Control"] == "no-store"
        assert payload["updates"][0]["view"]["role"] == "police"
        assert "opponent_position" not in json.dumps(payload)
    finally:
        server.shutdown()
        server.server_close()
        thread.join(2)


def test_live_server_refuses_non_loopback_binding(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="loopback"):
        build_live_server(tmp_path / "live.json", "0.0.0.0", 8765)


def test_reviewed_live_and_replay_screenshots_are_retained() -> None:
    for name in ("live-gui-local-truth.jpg", "replay-verified-ok.jpg"):
        payload = (PROJECT_ROOT / "docs" / "images" / name).read_bytes()
        assert payload.startswith(b"\xff\xd8\xff") and payload.endswith(b"\xff\xd9")
        assert 20_000 < len(payload) < 1_000_000
