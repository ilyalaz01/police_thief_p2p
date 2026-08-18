"""Export operation: copy a validated file set into a new empty output directory.

The exporter refuses a non-empty output directory to prevent accidental
overwrites and checks that no output path escapes the requested root.
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path

from tools.submission_export.planner import plan as run_plan


def export_to(
    source: Path | dict[str, object],
    output_dir: Path,
    repo_root: Path,
) -> dict[str, object]:
    """Validate a manifest, copy files, and write the export manifest.

    Args:
        source: Manifest path or already-parsed dict.
        output_dir: Destination directory (must exist and be empty).
        repo_root: Absolute path to the repository root.

    Returns:
        The deterministic plan dict that was exported.

    Raises:
        FileNotFoundError: *output_dir* does not exist.
        ValueError: *output_dir* is non-empty or a destination path escapes it.
        ManifestError, PathViolationError: Propagated from the plan step.
    """
    _assert_output_ready(output_dir)
    export_plan = run_plan(source, repo_root)
    for entry in export_plan["files"]:
        posix_path = str(entry["path"])
        dest = output_dir / posix_path
        _assert_within_root(dest, output_dir)
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(repo_root / posix_path, dest)
    _write_manifest(output_dir, export_plan)
    return export_plan


def _assert_output_ready(output_dir: Path) -> None:
    """Raise if output_dir is absent, not a directory, or non-empty."""
    if not output_dir.exists():
        raise FileNotFoundError(f"output directory does not exist: {output_dir}")
    if not output_dir.is_dir():
        raise ValueError(f"output path is not a directory: {output_dir}")
    if any(output_dir.iterdir()):
        raise ValueError(
            "output directory must be empty; refusing to overwrite existing content"
        )


def _assert_within_root(dest: Path, output_dir: Path) -> None:
    """Raise ValueError if dest resolves outside output_dir."""
    try:
        dest.resolve().relative_to(output_dir.resolve())
    except ValueError as exc:
        raise ValueError(f"output path escapes output root: {dest.name!r}") from exc


def _write_manifest(output_dir: Path, export_plan: dict[str, object]) -> None:
    """Write the export plan as export_manifest.json in the output root."""
    manifest_path = output_dir / "export_manifest.json"
    manifest_path.write_text(
        json.dumps(export_plan, indent=2, sort_keys=True),
        encoding="utf-8",
    )
