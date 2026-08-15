"""Commit verification and deterministic revealed-action replay."""

from __future__ import annotations

from typing import Any

from ..models import Position
from .crypto import verify_records


def verify_audit(records: list[dict[str, Any]]) -> dict[str, Any]:
    ok, failed = verify_records(records)
    steps = [record["payload"].get("step") for record in records]
    monotonic = steps == sorted(steps) and len(steps) == len(set(steps))
    positions_valid = all(
        record["payload"].get("type") == "system_spec"
        or (
            isinstance(record["payload"].get("position"), list)
            and len(record["payload"]["position"]) == 2
            and all(isinstance(v, int) for v in record["payload"]["position"])
        )
        for record in records
    )
    return {
        "verified": ok and monotonic and positions_valid,
        "failed_commit_indices": failed,
        "monotonic_steps": monotonic,
        "positions_valid": positions_valid,
        "steps": steps,
    }


def position(value: list[int]) -> Position:
    return Position(value[0], value[1])


def replay_sequence(records: list[dict[str, Any]], board_config: dict[str, Any]) -> dict[str, Any]:
    """Verify revealed local transitions without exposing them during live play."""
    commits_ok, failed = verify_records(records)
    audit = {"verified": commits_ok, "failed_commit_indices": failed}
    positions = {
        "police": position(board_config["police_start"]),
        "thief": position(board_config["thief_start"]),
    }
    barriers = {position(value) for value in board_config.get("blocked_cells", [])}
    errors: list[str] = []

    def replay_order(record: dict[str, Any]) -> tuple[int, int]:
        payload = record["payload"]
        sender = payload.get("sender") or record.get("_audit_sender")
        return payload["step"], 0 if sender == "thief" else 1

    for record in sorted(records, key=replay_order):
        payload = record["payload"]
        if payload.get("type") == "system_spec":
            continue
        sender = payload.get("sender") or record.get("_audit_sender")
        revealed = position(payload["position"])
        if sender not in positions:
            errors.append(f"step {payload.get('step')}: unknown sender")
            continue
        previous = positions[sender]
        action = payload.get("action")
        if action is None and isinstance(payload.get("move"), str):
            kind, _, direction = payload["move"].partition(":")
            barrier = None
            if kind == "BARRIER" and direction in {"N", "S", "E", "W"}:
                dr, dc = {"N": (-1, 0), "S": (1, 0), "E": (0, 1), "W": (0, -1)}[direction]
                barrier = [previous.row + dr, previous.col + dc]
            action = {
                "type": {"MOVE": "move", "HOLD": "stay", "BARRIER": "barrier"}.get(kind),
                "direction": None if direction == "-" else direction,
                "barrier": barrier,
            }
        expected = previous
        if action:
            kind = action.get("type")
            if kind == "move":
                delta = {"N": (-1, 0), "S": (1, 0), "E": (0, 1), "W": (0, -1)}.get(
                    action.get("direction")
                )
                if delta is None:
                    errors.append(f"step {payload['step']}: invalid direction")
                else:
                    expected = Position(previous.row + delta[0], previous.col + delta[1])
            elif kind == "barrier":
                target = position(action["barrier"])
                if abs(target.row - previous.row) + abs(target.col - previous.col) != 1:
                    errors.append(f"step {payload['step']}: non-adjacent barrier")
                barriers.add(target)
            elif kind != "stay":
                errors.append(f"step {payload['step']}: invalid action")
        if expected != revealed:
            errors.append(f"step {payload['step']}: position transition mismatch")
        if not (
            0 <= revealed.row < board_config["board_size"]
            and 0 <= revealed.col < board_config["board_size"]
        ):
            errors.append(f"step {payload['step']}: out of bounds")
        if action and action.get("type") == "move" and revealed in barriers:
            errors.append(f"step {payload['step']}: moved into barrier")
        positions[sender] = revealed
    return {**audit, "verified": audit["verified"] and not errors, "physics_errors": errors}
