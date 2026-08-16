"""Phase 4B CLI output and real FastMCP preflight checks."""

import json
import time
from pathlib import Path

import pytest
from interop_test_support import free_port, profile

from police_thief_lab.interop.runtime import PeerRuntime
from police_thief_lab.interop.transport import McpPeerClient, discover_tools, start_server


def test_cli_run_peer_creates_missing_output_parent(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    from police_thief_lab.interop import runtime as runtime_module

    monkeypatch.setattr(PeerRuntime, "run", lambda self: {"ok": False, "phase": "failed"})
    profile_path = tmp_path / "profile.json"
    profile_path.write_text(json.dumps(profile().object()))
    output = tmp_path / "missing" / "nested" / "result.json"
    status = runtime_module.run_peer(
        "police",
        profile_path,
        "127.0.0.1",
        free_port(),
        "http://127.0.0.1:1/mcp",
        "http://127.0.0.1:1/mcp",
        tmp_path / "artifacts",
        output,
    )
    assert status == 1
    assert json.loads(output.read_text()) == {"ok": False, "phase": "failed"}


def test_real_fastmcp_origin_preflight_discovers_normal_four_tools() -> None:
    port = free_port()
    start_server("preflight", "127.0.0.1", port)
    expected = ["negotiate", "receive_control", "receive_turn", "submit_audit"]
    client = McpPeerClient(f"http://127.0.0.1:{port}/mcp", 5.0, 0.01)
    discovered: list[str] | None = None
    for _attempt in range(100):
        try:
            discovered = discover_tools(client.url)
            break
        except Exception:
            time.sleep(0.01)
    assert discovered == expected
