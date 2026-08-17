"""Atomic bounded storage for role-local Live GUI updates."""

from __future__ import annotations

import json
import math
import threading
from collections import deque
from pathlib import Path
from typing import Any

from .models import RoleLocalView, TurnBanner

_ROOT_FIELDS = {"schema_version", "updates"}
_UPDATE_FIELDS = {"revision", "view"}
_VIEW_FIELDS = {
    "board_size",
    "role",
    "own_position",
    "blocked_cells",
    "barriers",
    "belief",
    "banner",
    "step",
}


def _pair(value: Any, label: str, size: int) -> tuple[int, int]:
    """Compute the internal pair step used by module."""
    if not isinstance(value, list) or len(value) != 2 or not all(
        isinstance(part, int) for part in value
    ):
        raise ValueError(f"{label} must be a two-integer list")
    pair = value[0], value[1]
    if any(not 0 <= part < size for part in pair):
        raise ValueError(f"{label} must be on the board")
    return pair


def _view(raw: Any) -> RoleLocalView:
    """Compute the internal view step used by module."""
    if not isinstance(raw, dict) or set(raw) != _VIEW_FIELDS:
        raise ValueError("live view fields are not the approved exact set")
    size = raw["board_size"]
    if not isinstance(size, int) or size < 1:
        raise ValueError("board_size must be a positive integer")
    if raw["role"] not in {"police", "thief"}:
        raise ValueError("role must be police or thief")
    if raw["banner"] not in {item.value for item in TurnBanner}:
        raise ValueError("unknown live banner")
    if not isinstance(raw["step"], int) or raw["step"] < 0:
        raise ValueError("step must be a non-negative integer")
    blocked = tuple(_pair(item, "blocked cell", size) for item in raw["blocked_cells"])
    barriers = tuple(_pair(item, "barrier", size) for item in raw["barriers"])
    belief = []
    for item in raw["belief"]:
        if not isinstance(item, list) or len(item) != 3:
            raise ValueError("belief entry must contain row, column, probability")
        cell = _pair(item[:2], "belief cell", size)
        probability = item[2]
        if not isinstance(probability, int | float) or not math.isfinite(probability):
            raise ValueError("belief probability must be finite")
        if probability < 0:
            raise ValueError("belief probability must be non-negative")
        belief.append((*cell, float(probability)))
    return RoleLocalView(
        size,
        raw["role"],
        _pair(raw["own_position"], "own position", size),
        blocked,
        barriers,
        tuple(belief),
        raw["banner"],
        raw["step"],
    )


def load_live_feed(path: Path) -> dict[str, Any]:
    """Read and strictly sanitize one feed before it reaches an HTTP client."""
    raw = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict) or set(raw) != _ROOT_FIELDS:
        raise ValueError("live feed fields are not the approved exact set")
    if raw["schema_version"] != "1.0" or not isinstance(raw["updates"], list):
        raise ValueError("unsupported live feed schema")
    updates = []
    previous = 0
    for item in raw["updates"]:
        if not isinstance(item, dict) or set(item) != _UPDATE_FIELDS:
            raise ValueError("live update fields are not the approved exact set")
        revision = item["revision"]
        if not isinstance(revision, int) or revision <= previous:
            raise ValueError("live revisions must be increasing positive integers")
        previous = revision
        updates.append({"revision": revision, "view": _view(item["view"]).to_object()})
    return {"schema_version": "1.0", "updates": updates}


class LiveViewPublisher:
    """Publish a bounded role-safe history with atomic same-directory replacement."""

    def __init__(self, path: Path, history_limit: int = 32) -> None:
        """Initialize LiveViewPublisher with its validated setup values and private state."""
        if history_limit < 1:
            raise ValueError("history_limit must be positive")
        self.path = path
        self._updates: deque[dict[str, Any]] = deque(maxlen=history_limit)
        self._revision = 0
        self._lock = threading.Lock()

    def publish(self, view: RoleLocalView) -> None:
        """Append one sanitized view and replace the JSON feed atomically."""
        with self._lock:
            self._revision += 1
            self._updates.append({"revision": self._revision, "view": view.to_object()})
            payload = {"schema_version": "1.0", "updates": list(self._updates)}
            self.path.parent.mkdir(parents=True, exist_ok=True)
            temporary = self.path.with_suffix(self.path.suffix + ".tmp")
            temporary.write_text(
                json.dumps(payload, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
            temporary.replace(self.path)
