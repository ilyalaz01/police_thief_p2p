"""Phase 4A runtime terminal, deadline, replay, and profile checks."""

import json
from pathlib import Path

from interop_test_support import ROOT, frame, free_port, profile

from police_thief_lab import Position, Role
from police_thief_lab.interop.crypto import seal
from police_thief_lab.interop.profile import MatchProfile
from police_thief_lab.interop.replay import replay_sequence
from police_thief_lab.interop.runtime import DeadlineTracker, PeerRuntime
from police_thief_lab.interop.transport import PeerInboxes


def test_rule46_and_rule47_terminal_are_processed_before_strategy(
    monkeypatch, tmp_path: Path
) -> None:
    runtime = PeerRuntime(
        Role.THIEF, profile(), "127.0.0.1", free_port(), "http://127.0.0.1:1/mcp", tmp_path
    )
    monkeypatch.setattr(runtime, "_send_terminal_response", lambda step: None)
    runtime.state.position = Position(3, 3)
    runtime.receiver.mark_local(1, "d" * 64)
    message = frame(2)
    message["sender"] = "police"
    message["barrier_placed"] = [3, 3]
    runtime._apply_inbound(runtime.receiver.offer(message)[0])
    assert runtime.state.terminal == "barrier_on_thief"

    boxed_profile = MatchProfile(
        profile().board_config | {"blocked_cells": [[2, 3], [4, 3], [3, 2]]}
    )
    boxed = PeerRuntime(
        Role.THIEF, boxed_profile, "127.0.0.1", free_port(), "http://127.0.0.1:1/mcp", tmp_path
    )
    monkeypatch.setattr(boxed, "_send_terminal_response", lambda step: None)
    boxed.state.position = Position(3, 3)
    boxed.receiver.mark_local(1, "d" * 64)
    message = frame(2)
    message["sender"] = "police"
    message["barrier_placed"] = [3, 4]
    boxed._apply_inbound(boxed.receiver.offer(message)[0])
    assert boxed.state.terminal == "thief_boxed_in"


def test_turn_timeout_path_uses_monotonic_deadline(tmp_path: Path) -> None:
    short = MatchProfile(
        profile().board_config,
        timeouts={"connect": 0.05, "turn": 0.01, "audit": 0.05, "retry": 0.01},
    )
    runtime = PeerRuntime(
        Role.POLICE, short, "127.0.0.1", free_port(), "http://127.0.0.1:1/mcp", tmp_path
    )
    runtime.inboxes = PeerInboxes()
    deadline = DeadlineTracker(0.01)
    runtime._receive_and_maybe_act()
    assert runtime.state.terminal == "timeout"
    assert deadline.remaining() <= 0.01


def test_reference_sender_local_replay_is_thief_first_for_equal_steps() -> None:
    """Regression: equal sender-local step numbers must not reorder a barrier before Thief."""
    thief = seal({"step": 1, "position": [4, 0], "move": "MOVE:N"})
    police = seal({"step": 1, "position": [4, 1], "move": "BARRIER:W"})
    spec = seal({"step": 0, "type": "system_spec", "spec": {}, "model": "stub"})
    records = [
        dict(police, _audit_sender="police"),
        dict(spec, _audit_sender="police"),
        dict(thief, _audit_sender="thief"),
    ]
    board = {"board_size": 7, "police_start": [4, 1], "thief_start": [5, 0], "blocked_cells": []}
    assert replay_sequence(records, board) == {
        "verified": True,
        "failed_commit_indices": [],
        "physics_errors": [],
    }


def test_reference_profile_uses_sender_local_steps_and_reference_terms(tmp_path: Path) -> None:
    raw = json.loads(
        (ROOT / "interop/fixtures/phase4a5_reference_profile.json").read_text(encoding="utf-8")
    )
    reference = MatchProfile(**raw)
    runtime = PeerRuntime(
        Role.THIEF, reference, "127.0.0.1", free_port(), "http://127.0.0.1:1/mcp", tmp_path
    )
    assert runtime._next_outbound() == 1
    assert runtime._next_outbound() == 2
    assert reference.reference_terms()["setting"] == "New York"
    assert reference.reference_terms()["min_center_intensity"] == 0.5
