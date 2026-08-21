"""Kit SPEC 3.1 thief concession shape and operator declaration identity."""

from dataclasses import replace
from pathlib import Path

import pytest

from police_thief_lab import Position, Role
from police_thief_lab.interop.runtime import PeerRuntime
from police_thief_lab.interop.runtime_identity import peer_identity_object, validate_hint
from tests.support.interop_test_support import free_port, profile

REQUIRED_WIRE_KEYS = {"step", "sender", "hint", "smell_grid", "commit", "timestamp"}
DECLARATION = {
    "group_id": "alpha-01",
    "group_name": "Alpha",
    "members": ["Student One"],
    "repos": {"cop": "https://github.com/example/cop", "thief": "https://github.com/example/thief"},
    "mcp_servers": {"cop": "https://cop.example/mcp", "thief": "https://thief.example/mcp"},
    "llm_model": "deterministic-python",
    "spec": {"cpu_type": "CPU", "cpu_cores": 8},
}


def _thief(tmp_path: Path) -> PeerRuntime:
    """Build one offline thief runtime on the negotiated sender-local numbering."""
    sender_local = replace(profile(), step_numbering="sender_local")
    return PeerRuntime(
        Role.THIEF, sender_local, "127.0.0.1", free_port(), "http://127.0.0.1:1/mcp", tmp_path
    )


def test_thief_terminal_carries_its_own_final_cell(monkeypatch, tmp_path: Path) -> None:
    runtime = _thief(tmp_path)
    sent: list[dict] = []
    monkeypatch.setattr(
        runtime.client, "call", lambda tool, value, timeout=None: sent.append(value) or 1.0
    )
    runtime.state.position = Position(5, 4)
    runtime.state.terminal = "barrier_on_thief"
    runtime._send_terminal_response(3)
    assert len(sent) == 1
    message = sent[0]
    assert message["claim_response"] == {
        "claim": [5, 4],
        "caught": True,
        "reason": "barrier_on_thief",
    }
    assert set(message) >= REQUIRED_WIRE_KEYS
    assert message["smell_grid"] == {}
    assert runtime.records[-1]["payload"]["position"] == [5, 4]


def test_terminal_claim_matches_the_revealed_record(monkeypatch, tmp_path: Path) -> None:
    runtime = _thief(tmp_path)
    sent: list[dict] = []
    monkeypatch.setattr(
        runtime.client, "call", lambda tool, value, timeout=None: sent.append(value) or 1.0
    )
    runtime.state.position = Position(0, 6)
    runtime.state.terminal = "thief_boxed_in"
    runtime._send_terminal_response(9)
    assert sent[0]["claim_response"]["claim"] == runtime.records[-1]["payload"]["position"]


def test_identity_without_a_declaration_keeps_the_self_test_shape() -> None:
    identity = peer_identity_object("thief", "https://team.example/mcp", "abc123")
    assert identity["group_id"] == "local-thief"
    assert identity["members"] == []
    assert identity["mcp_servers"] == {"thief": "https://team.example/mcp"}
    assert identity["github_commit"] == "abc123"


def test_declaration_supplies_members_repositories_and_hardware() -> None:
    identity = peer_identity_object(
        "police", "https://live.example/mcp", "abc123", declaration=DECLARATION
    )
    assert identity["members"] == ["Student One"]
    assert identity["repos"]["cop"] == "https://github.com/example/cop"
    assert identity["spec"]["cpu_cores"] == 8
    assert identity["mcp_servers"]["cop"] == "https://live.example/mcp"
    assert identity["mcp_servers"]["thief"] == "https://thief.example/mcp"
    assert DECLARATION["mcp_servers"]["cop"] == "https://cop.example/mcp"


def test_a_conflicting_command_line_group_is_refused_rather_than_merged() -> None:
    with pytest.raises(ValueError, match="group_id"):
        peer_identity_object(
            "police", "https://live.example/mcp", "abc", "other-id", declaration=DECLARATION
        )


def test_hint_longer_than_the_negotiated_cap_is_refused() -> None:
    assert validate_hint("short hint", 15) == "short hint"
    with pytest.raises(ValueError, match="15-word"):
        validate_hint(" ".join(["word"] * 16), 15)
