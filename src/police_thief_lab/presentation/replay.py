"""Build sanitized replay frames from a completed revealed artifact log."""

from __future__ import annotations

from typing import Any

from ..interop.replay import replay_sequence
from .models import ReplayFrame, ReplayView


def _pair(value: Any, label: str) -> tuple[int, int]:
    """Compute the internal pair step used by module."""
    if (
        not isinstance(value, list | tuple)
        or len(value) != 2
        or any(not isinstance(part, int) for part in value)
    ):
        raise ValueError(f"{label} must be a two-integer coordinate")
    return value[0], value[1]


def _board_config(config: dict[str, Any]) -> dict[str, Any]:
    """Compute the internal board config step used by module."""
    source = config.get("board_config", config)
    if not isinstance(source, dict):
        raise ValueError("board_config must be a JSON object")
    size = source.get("board_size")
    if not isinstance(size, int) or size < 1:
        raise ValueError("board_size must be a positive integer")
    police = _pair(source.get("cop_start", source.get("police_start")), "cop_start")
    thief = _pair(source.get("thief_start"), "thief_start")
    blocked = [_pair(cell, "blocked cell") for cell in source.get("blocked_cells", [])]
    if any(not 0 <= part < size for cell in (police, thief, *blocked) for part in cell):
        raise ValueError("configured coordinates must be on the board")
    return {
        "board_size": size,
        "police_start": list(police),
        "thief_start": list(thief),
        "blocked_cells": [list(cell) for cell in blocked],
    }


def _ordered(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Compute the internal ordered step used by module."""
    def key(record: dict[str, Any]) -> tuple[int, int]:
        """Return the deterministic ordering key for one replay record."""
        payload = record.get("payload", {})
        step = payload.get("step")
        sender = payload.get("sender") or record.get("_audit_sender")
        return (step if isinstance(step, int) else 2**31, 0 if sender == "thief" else 1)

    return sorted(records, key=key)


def _frames(records: list[dict[str, Any]], board: dict[str, Any]) -> tuple[ReplayFrame, ...]:
    """Compute the internal frames step used by module."""
    positions = {
        "police": tuple(board["police_start"]),
        "thief": tuple(board["thief_start"]),
    }
    blocked = tuple(sorted(tuple(cell) for cell in board["blocked_cells"]))
    barriers: set[tuple[int, int]] = set()
    frames = [ReplayFrame(0, 0, positions["police"], positions["thief"], blocked, (), None)]
    for record in _ordered(records):
        payload = record.get("payload", {})
        if payload.get("type") == "system_spec":
            continue
        sender = payload.get("sender") or record.get("_audit_sender")
        if sender not in positions or not isinstance(payload.get("step"), int):
            continue
        try:
            positions[sender] = _pair(payload.get("position"), "revealed position")
            action = payload.get("action") or {}
            if action.get("type") == "barrier":
                barriers.add(_pair(action.get("barrier"), "barrier"))
        except ValueError:
            continue
        frames.append(
            ReplayFrame(
                len(frames),
                payload["step"],
                positions["police"],
                positions["thief"],
                blocked,
                tuple(sorted(barriers)),
                sender,
            )
        )
    return tuple(frames)


def build_replay(log: dict[str, Any], config: dict[str, Any]) -> ReplayView:
    """Verify a revealed log and build a nonce-free, post-game playback model."""
    records = log.get("records")
    if not isinstance(records, list):
        raise ValueError("log records must be a list")
    board = _board_config(config)
    try:
        check = replay_sequence(records, board)
        failed = tuple(check["failed_commit_indices"])
        errors = tuple(check["physics_errors"])
        verified = bool(check["verified"])
    except (KeyError, TypeError, ValueError) as exc:
        failed, errors, verified = (), (f"malformed record: {type(exc).__name__}",), False
    summary = log.get("summary") if isinstance(log.get("summary"), dict) else {}
    return ReplayView(
        game_id=str(log.get("game_id", "unknown-game")),
        board_size=board["board_size"],
        result=str(summary.get("result", "unknown")),
        frames=_frames(records, board),
        verdict="Verified OK" if verified else "TAMPERED",
        failed_commit_indices=failed,
        physics_errors=errors,
    )
