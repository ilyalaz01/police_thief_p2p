"""Phase 4A real two-process localhost system check."""

import json
import subprocess
import sys
from pathlib import Path

from tests.support.interop_test_support import ROOT, free_port


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
