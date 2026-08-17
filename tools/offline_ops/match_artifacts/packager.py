"""Redacted manifest/report rendering and atomic packaging for package-match.

Manifests and reports render only filenames, byte lengths, SHA-256 values,
validator identities, durations, statuses, and exit codes — never file
contents, identity blocks, audit records, commit values, MCP URLs, or
nonce values.
"""

from __future__ import annotations

import hashlib
import json
import uuid
from pathlib import Path

from tools.offline_ops.models import GateReport

_MANIFEST_SCHEMA_VERSION = "1.0"


def build_manifest(artifact_files: list[Path], validation: GateReport) -> dict[str, object]:
    """Build the redacted JSON validation manifest for a package."""
    return {
        "schema_version": _MANIFEST_SCHEMA_VERSION,
        "files": [
            {
                "filename": file.name,
                "byte_length": file.stat().st_size,
                "sha256": hashlib.sha256(file.read_bytes()).hexdigest(),
            }
            for file in artifact_files
        ],
        "checks": [
            {
                "check_id": check.check_id,
                "status": check.status.value,
                "duration_seconds": check.duration_seconds,
                "exit_code": check.exit_code,
            }
            for check in validation.checks
        ],
        "overall_exit_code": validation.exit_code,
    }


def render_markdown(manifest: dict[str, object]) -> str:
    """Render ``manifest`` as an equivalent redacted Markdown report."""
    lines = [
        "# Match Artifact Package Report",
        "",
        f"Schema version: {manifest['schema_version']}",
        f"Overall exit code: {manifest['overall_exit_code']}",
        "",
        "## Files",
        "",
        "| Filename | Bytes | SHA-256 |",
        "| --- | ---: | --- |",
    ]
    for entry in manifest["files"]:
        lines.append(f"| {entry['filename']} | {entry['byte_length']} | {entry['sha256']} |")
    lines += ["", "## Checks", ""]
    lines += ["| Check | Status | Duration (s) | Exit code |", "| --- | --- | ---: | ---: |"]
    for check in manifest["checks"]:
        lines.append(
            f"| {check['check_id']} | {check['status']} | "
            f"{check['duration_seconds']:.3f} | {check['exit_code']} |"
        )
    lines.append("")
    return "\n".join(lines)


def write_package(
    artifact_files: list[Path], manifest: dict[str, object], markdown: str, output: Path
) -> None:
    """Atomically write ``output``, containing only the given artifact
    files plus the manifest and report; ``output`` itself is never
    touched until the whole package is staged.

    Raises:
        OSError: On any staging or rename failure; the staging directory
            is removed and ``output`` is left untouched.
    """
    staging = output.parent / f".{output.name}.partial-{uuid.uuid4().hex[:8]}"
    staging.mkdir(parents=True)
    try:
        for source in artifact_files:
            (staging / source.name).write_bytes(source.read_bytes())
        (staging / "package_manifest.json").write_text(
            json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        (staging / "package_report.md").write_text(markdown, encoding="utf-8")
        staging.rename(output)
    except OSError:
        _remove_flat_directory(staging)
        raise


def _remove_flat_directory(directory: Path) -> None:
    for child in directory.iterdir():
        child.unlink()
    directory.rmdir()
