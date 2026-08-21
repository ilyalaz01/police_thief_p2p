"""Phase 4A in-process runtime and MCP surface checks."""

import threading
from dataclasses import replace
from pathlib import Path

from police_thief_lab import Role
from police_thief_lab.interop.profile import MatchProfile
from police_thief_lab.interop.runtime import PeerRuntime
from police_thief_lab.interop.transport import McpPeerClient, start_server
from tests.support.interop_test_support import free_port, profile


def test_complete_network_runtime_in_two_isolated_peer_objects(tmp_path: Path) -> None:
    """Play one complete game over the real MCP surface with the accepted defaults.

    The accepted Thief default survives to the move limit against the frozen Police, so this
    game is a full-length one rather than the short capture the earlier integration default
    produced. The per-turn and join budgets below are sized for that length on a slow loopback;
    they bound the harness only and change no negotiated value.
    """
    police_port, thief_port = free_port(), free_port()
    shared = replace(
        profile(), timeouts={"connect": 20.0, "turn": 15.0, "audit": 10.0, "retry": 0.05}
    )
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
        thread.join(180)
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
