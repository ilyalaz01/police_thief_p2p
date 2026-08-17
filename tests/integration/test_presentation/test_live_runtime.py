"""Peer-runtime to role-local Live GUI integration tests."""

import json
from pathlib import Path

from police_thief_lab.presentation.live_feed import load_live_feed
from tests.support.interop_test_support import _run_reference_pair


def test_complete_peer_pair_emits_only_role_legal_live_states(tmp_path: Path) -> None:
    police_path = tmp_path / "views" / "police.json"
    thief_path = tmp_path / "views" / "thief.json"

    police, thief = _run_reference_pair(
        tmp_path,
        "capture",
        live_view_paths=(police_path, thief_path),
    )

    assert police["ok"] and thief["ok"]
    for role, path in (("police", police_path), ("thief", thief_path)):
        feed = load_live_feed(path)
        views = [item["view"] for item in feed["updates"]]
        banners = {view["banner"] for view in views}
        assert {"YOUR TURN", "LOCKED", "GAME OVER"} <= banners
        assert all(view["role"] == role for view in views)
        raw = path.read_text(encoding="utf-8")
        assert "opponent_position" not in raw
        assert all(term not in raw for term in ("nonce", "commit", "wire", "opponent_url"))
        assert json.loads(raw)["updates"][-1]["view"]["banner"] == "GAME OVER"

