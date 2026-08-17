"""Writers for legacy local artifact bundles."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .artifact_encoding import pretty_bytes


def write_artifacts(directory: Path, game_id: str, game_number: int,
                    profile: dict[str, Any], log: dict[str, Any],
                    result: dict[str, Any]) -> list[Path]:
    """Write the four legacy local artifacts and return their ordered paths."""
    values = {f"declaration_{game_id}.json": {"game_id": game_id, "kind": "UNCOUNTED_LOCALHOST"},
              f"config_{game_id}_g{game_number:02d}.json": profile,
              f"log_{game_id}_g{game_number:02d}.json": log,
              f"result_{game_id}.json": result}
    directory.mkdir(parents=True, exist_ok=True)
    paths = []
    for name, value in values.items():
        path = directory / name
        path.write_bytes(pretty_bytes(value))
        paths.append(path)
    return paths
