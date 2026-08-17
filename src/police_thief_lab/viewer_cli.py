"""Offline command line for building the artifact-backed Replay Viewer."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from .presentation import build_replay, render_replay_html


def build_parser() -> argparse.ArgumentParser:
    """Build the viewer parser without reading files or opening a browser."""
    parser = argparse.ArgumentParser(
        description="Build a standalone post-game Replay Viewer from revealed artifacts."
    )
    subcommands = parser.add_subparsers(dest="command", required=True)
    replay = subcommands.add_parser("replay", help="verify and render one completed sub-game")
    replay.add_argument("--log", type=Path, required=True, help="schema 1.1 revealed log JSON")
    replay.add_argument("--config", type=Path, required=True, help="matching config artifact JSON")
    replay.add_argument("--output", type=Path, required=True, help="standalone HTML output path")
    return parser


def _object(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path.name} must contain a JSON object")
    return value


def main(argv: list[str] | None = None) -> int:
    """Verify input, write a nonce-free viewer, and fail closed on tampering."""
    args = build_parser().parse_args(argv)
    replay = build_replay(_object(args.log), _object(args.config))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(render_replay_html(replay), encoding="utf-8")
    return 0 if replay.verdict == "Verified OK" else 2


if __name__ == "__main__":
    raise SystemExit(main())
