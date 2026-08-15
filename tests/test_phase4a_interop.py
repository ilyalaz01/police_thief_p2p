"""Phase 4A crypto, delivery, negotiation, boundary, audit, and artifact checks."""

from __future__ import annotations

import json
import socket
import subprocess
import sys
import threading
from dataclasses import fields
from pathlib import Path

import pytest

from police_thief_lab import GameConfig, Observation, Position, Role, Simulator
from police_thief_lab.interop.artifacts import (
    canonical_sha256,
    consensus_sha256,
    pretty_bytes,
    write_artifacts,
)
from police_thief_lab.interop.crypto import canonical_json, hcommit, seal, verify_records
from police_thief_lab.interop.profile import MatchProfile
from police_thief_lab.interop.protocol import Equivocation, ProtocolViolation, TurnInbox
from police_thief_lab.interop.replay import replay_sequence, verify_audit
from police_thief_lab.interop.runtime import DeadlineTracker, PeerRuntime
from police_thief_lab.interop.transport import McpPeerClient, PeerInboxes, start_server
from police_thief_lab.policies.tactical import ScentTacticalPolice

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


def test_all_hcommit_golden_vectors_and_extra_fields() -> None:
    vectors = json.loads(
        (ROOT / "interop/golden_vectors/hcommit_reference_vs_kit.json").read_text(encoding="utf-8")
    )["vectors"]
    for vector in vectors:
        assert canonical_json(vector["payload"]) == vector["canonical"]
        assert hcommit(vector["payload"], vector["nonce"]) == vector["expected_sha256"]
    payload = {"step": 1, "hint": "עברית🙂", "float": 1e-7}
    assert hcommit(payload, "n") != hcommit(payload | {"extra": None}, "n")


def test_delivery_duplicate_equivocation_buffer_stale_and_window() -> None:
    inbox = TurnInbox(window=2)
    assert inbox.offer(frame(2, "b" * 64)) == []
    ready = inbox.offer(frame(1))
    assert [message.step for message in ready] == [1, 2]
    assert inbox.offer(frame(1)) == []
    assert inbox.absorbed == 1
    with pytest.raises(Equivocation):
        inbox.offer(frame(2, "c" * 64))
    with pytest.raises(ProtocolViolation):
        inbox.offer(frame(6))


def test_profile_requires_byte_identical_config() -> None:
    own = profile()
    own.verify_agreement(own.agreement("thief"))
    changed = own.agreement("thief")
    changed["identity"]["config_bytes_hex"] += "0a"
    with pytest.raises(ValueError, match="byte-identical"):
        own.verify_agreement(changed)


def test_strategy_boundary_contains_only_legal_observation() -> None:
    simulator = Simulator(GameConfig())
    simulator.apply(simulator.observe(Role.THIEF).legal_actions[-1])
    observation = simulator.observe(Role.POLICE)
    names = {field.name for field in fields(Observation)}
    assert not {"world_state", "opponent_position", "audit", "remote_peer"} & names
    assert ScentTacticalPolice(1).choose_action(observation) in observation.legal_actions


def test_tampered_nonce_payload_and_replay_are_rejected() -> None:
    record = seal({"step": 1, "position": [1, 1], "hint": "🙂"}, "nonce")
    assert verify_records([record]) == (True, [])
    bad_nonce = record | {"nonce": "changed"}
    bad_payload = record | {"payload": record["payload"] | {"position": [1, 2]}}
    assert not verify_audit([bad_nonce])["verified"]
    assert not verify_audit([bad_payload])["verified"]
    forged = seal(
        {
            "step": 1,
            "sender": "thief",
            "position": [6, 6],
            "action": {"type": "move", "direction": "N", "barrier": None},
        }
    )
    assert not replay_sequence([forged], profile().board_config)["verified"]


def test_artifact_grammars_roundtrip_and_serializations_are_distinct(tmp_path: Path) -> None:
    value = {"z": "שלום", "a": 0.9}
    assert pretty_bytes(value) != canonical_json(value).encode()
    assert canonical_sha256(value) != consensus_sha256(value)
    paths = write_artifacts(
        tmp_path, "game", 3, profile().object(), {"records": []}, {"verified": True}
    )
    assert {path.name for path in paths} == {
        "declaration_game.json",
        "config_game_g03.json",
        "log_game_g03.json",
        "result_game.json",
    }
    assert all(json.loads(path.read_text(encoding="utf-8")) for path in paths)


def test_complete_network_runtime_in_two_isolated_peer_objects(tmp_path: Path) -> None:
    police_port, thief_port = free_port(), free_port()
    shared = profile()
    police = PeerRuntime(
        Role.POLICE,
        shared,
        "127.0.0.1",
        police_port,
        f"http://127.0.0.1:{thief_port}/mcp",
        tmp_path / "police",
        1,
    )
    thief = PeerRuntime(
        Role.THIEF,
        shared,
        "127.0.0.1",
        thief_port,
        f"http://127.0.0.1:{police_port}/mcp",
        tmp_path / "thief",
        1,
    )
    results = {}
    threads = [
        threading.Thread(target=lambda: results.setdefault("police", police.run())),
        threading.Thread(target=lambda: results.setdefault("thief", thief.run())),
    ]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(20)
    assert not any(thread.is_alive() for thread in threads)
    assert results["police"]["ok"] and results["thief"]["ok"]
    assert results["police"]["config_sha256"] == results["thief"]["config_sha256"]
    combined = results["police"]["events"] + results["thief"]["events"]
    sent = sorted(event["step"] for event in combined if event["event"] == "sent")
    assert sent[0] == 1
    assert thief.records[0]["payload"]["sender"] == "thief"
    assert all("opponent_position" not in record["payload"] for record in police.records)
    first = thief.state.own_scent
    assert max(dict(first).values()) == 0.8


def test_real_mcp_surface_queues_all_four_reference_calls() -> None:
    port = free_port()
    inboxes = start_server("police", "127.0.0.1", port)
    client = McpPeerClient(f"http://127.0.0.1:{port}/mcp", 5.0, 0.01)
    for tool, inbox in (
        ("negotiate", inboxes.agreements),
        ("receive_turn", inboxes.turns),
        ("submit_audit", inboxes.audits),
        ("receive_control", inboxes.controls),
    ):
        client.call(tool, {"unicode": "שלום🙂"})
        assert inbox.get(timeout=1) == {"unicode": "שלום🙂"}


def test_real_negotiation_mismatch_is_rejected_before_play(tmp_path: Path) -> None:
    police_port, thief_port = free_port(), free_port()
    police_profile = profile()
    thief_profile = MatchProfile(police_profile.board_config | {"thief_start": [4, 4]})
    police = PeerRuntime(
        Role.POLICE,
        police_profile,
        "127.0.0.1",
        police_port,
        f"http://127.0.0.1:{thief_port}/mcp",
        tmp_path / "police",
    )
    thief = PeerRuntime(
        Role.THIEF,
        thief_profile,
        "127.0.0.1",
        thief_port,
        f"http://127.0.0.1:{police_port}/mcp",
        tmp_path / "thief",
    )
    results = []
    threads = [
        threading.Thread(target=lambda runtime=runtime: results.append(runtime.run()))
        for runtime in (police, thief)
    ]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(10)
    assert len(results) == 2
    assert all(not result["ok"] and "mismatch" in result["error"] for result in results)


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


def test_two_real_independent_processes_complete_localhost_game(tmp_path: Path) -> None:
    police_port, thief_port = free_port(), free_port()
    profile_path = ROOT / "interop/fixtures/phase4a_local_profile.json"
    commands = []
    for role, own, other in (
        ("police", police_port, thief_port),
        ("thief", thief_port, police_port),
    ):
        commands.append(
            [
                sys.executable,
                "-m",
                "police_thief_lab.peer_cli",
                "--role",
                role,
                "--profile",
                str(profile_path),
                "--port",
                str(own),
                "--opponent-url",
                f"http://127.0.0.1:{other}/mcp",
                "--artifacts",
                str(tmp_path / role),
                "--output",
                str(tmp_path / f"{role}.json"),
            ]
        )
    processes = [subprocess.Popen(command, cwd=ROOT) for command in commands]
    statuses = [process.wait(timeout=25) for process in processes]
    assert statuses == [0, 0]
    outputs = [
        json.loads((tmp_path / f"{role}.json").read_text(encoding="utf-8"))
        for role in ("police", "thief")
    ]
    assert all(output["ok"] and output["phase"] == "verified" for output in outputs)
    assert outputs[0]["outcome"] == outputs[1]["outcome"]
