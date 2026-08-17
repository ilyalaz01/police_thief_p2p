"""CLI for preregistered local simulator runtime measurements."""

from __future__ import annotations

import argparse
import json
import os
import platform
from pathlib import Path

from .runtime_probe import (
    execute_design,
    load_design,
    memory_one_game,
    timing_one_game,
    warmup_one_game,
)


def _environment() -> dict[str, object]:
    """Return public-safe host characteristics without identity or absolute paths."""
    return {
        "logical_cpu_count": os.cpu_count(),
        "machine": platform.machine(),
        "python_version": platform.python_version(),
        "system": platform.system(),
    }


def _safe_output(root: Path, requested: str) -> Path:
    """Resolve a repository-contained new evidence output path."""
    if not requested or Path(requested).is_absolute():
        raise ValueError("output must be a repository-relative path")
    output = (root / requested).resolve()
    try:
        output.relative_to(root.resolve())
    except ValueError as exc:
        raise ValueError("output must remain inside the repository") from exc
    if output.exists():
        raise ValueError("output already exists; refusing to overwrite evidence")
    if not output.parent.is_dir() or output.parent.is_symlink():
        raise ValueError("output parent must be an existing ordinary directory")
    return output


def main(argv: list[str] | None = None) -> int:
    """Run the bounded design and write one new JSON evidence file."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--design", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--measured-at-utc", required=True)
    args = parser.parse_args(argv)
    root = Path(args.repo_root).resolve()
    try:
        design_path = (root / args.design).resolve()
        design_path.relative_to(root)
        design = load_design(design_path, root)
        output = _safe_output(root, args.output)
        report = execute_design(
            design, warmup_one_game, timing_one_game, memory_one_game, _environment()
        )
        report["measured_at_utc"] = args.measured_at_utc
        output.write_text(
            json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        parser.error(str(exc))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
