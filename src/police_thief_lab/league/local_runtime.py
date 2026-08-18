"""Run one unchanged Police/Thief peer pair as two localhost processes."""

from __future__ import annotations

import json
import multiprocessing
import socket
import time
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from ..interop.profile import MatchProfile
from ..interop.runtime import run_peer
from .identity import TeamDeclarationIdentity
from .series import SeriesSlot


def _free_port() -> int:
    """Reserve and release one loopback port for immediate local peer startup."""
    with socket.socket() as listener:
        listener.bind(("127.0.0.1", 0))
        return int(listener.getsockname()[1])


def _run_peer_process(
    role: str,
    profile_path: Path,
    port: int,
    opponent_port: int,
    artifact_dir: Path,
    output_path: Path,
    seed: int,
    group_id: str,
    group_name: str,
    commit: str,
) -> None:
    """Execute the existing file-oriented peer boundary in one child process."""
    own_url = f"http://127.0.0.1:{port}/mcp"
    status = run_peer(
        role,
        profile_path,
        "127.0.0.1",
        port,
        own_url,
        f"http://127.0.0.1:{opponent_port}/mcp",
        artifact_dir,
        output_path,
        seed,
        group_id,
        group_name,
        commit,
        False,
        None,
    )
    raise SystemExit(status)


def _read_result(path: Path) -> dict[str, Any]:
    """Load one terminal child result or fail without exposing its artifact bodies."""
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ValueError("localhost peer process did not retain a readable result") from exc
    if not isinstance(value, dict):
        raise ValueError("localhost peer process result must be an object")
    return value


def run_localhost_pair(
    slot: SeriesSlot,
    profile: MatchProfile,
    identities: Mapping[str, TeamDeclarationIdentity],
    commits: Mapping[str, str],
    artifact_root: Path,
    seed: int,
    watchdog_seconds: int,
) -> dict[str, dict[str, Any]]:
    """Run two independent loopback peers and return their terminal result objects."""
    artifact_root.mkdir(parents=True, exist_ok=True)
    profile_path = artifact_root / "match-profile.json"
    profile_path.write_bytes(profile.bytes())
    police_port, thief_port = _free_port(), _free_port()
    groups = {"police": slot.police_group, "thief": slot.thief_group}
    ports = {"police": (police_port, thief_port), "thief": (thief_port, police_port)}
    outputs = {role: artifact_root / f"{role}-result.json" for role in groups}
    context = multiprocessing.get_context("spawn")
    processes = []
    for role, group_id in groups.items():
        own_port, peer_port = ports[role]
        process = context.Process(
            target=_run_peer_process,
            args=(
                role,
                profile_path,
                own_port,
                peer_port,
                artifact_root / group_id,
                outputs[role],
                seed,
                group_id,
                identities[group_id].group_name,
                commits[group_id],
            ),
            name=f"localhost-g{slot.sub_game_number:02d}-{role}",
        )
        processes.append(process)
    for process in processes:
        process.start()
    deadline = time.monotonic() + watchdog_seconds
    for process in processes:
        process.join(max(0.0, deadline - time.monotonic()))
    if any(process.is_alive() for process in processes):
        for process in processes:
            if process.is_alive():
                process.terminate()
            process.join(5)
        raise TimeoutError("localhost sub-game watchdog expired")
    return {groups[role]: _read_result(outputs[role]) for role in groups}
