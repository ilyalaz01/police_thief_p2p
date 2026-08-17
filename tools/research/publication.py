"""Orchestrate deterministic research data, figures, analysis, and provenance."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from .design import load_design
from .render import analysis_markdown, summary_csv
from .runner import build_payload
from .svg import render_chart

OUTPUTS = {
    "raw": Path("results/research/phase4d9_sensitivity.json"),
    "summary": Path("results/research/phase4d9_summary.csv"),
    "board_figure": Path("assets/research/capture_by_board_size.svg"),
    "survival_figure": Path("assets/research/capture_by_survival_threshold.svg"),
    "notebook": Path("notebooks/POLICY_SENSITIVITY_ANALYSIS.md"),
}
SOURCE_FILES = (
    "tools/research/design.py", "tools/research/runner.py", "tools/research/statistics.py",
    "tools/research/svg.py", "tools/research/render.py", "tools/research/publication.py",
    "tools/research/cli.py",
)
FROZEN_FILES = (
    "src/police_thief_lab/models.py", "src/police_thief_lab/rules.py",
    "src/police_thief_lab/scent.py", "src/police_thief_lab/turns.py",
    "src/police_thief_lab/simulator.py", "src/police_thief_lab/policies/tactical.py",
    "src/police_thief_lab/interop/crypto.py",
)


def build_publication(design_path: Path, output_root: Path) -> dict[str, Any]:
    """Generate all curated artifacts and return their deterministic manifest."""
    design = load_design(design_path)
    payload = build_payload(design)
    values = {
        "raw": _json_bytes(payload),
        "summary": summary_csv(payload["summary"]),
        "board_figure": render_chart(
            payload["summary"], "board_size", (7, 9, 11), "Capture sensitivity to board size"
        ),
        "survival_figure": render_chart(
            payload["summary"], "survival_threshold", (35, 50, 70),
            "Capture sensitivity to survival threshold",
        ),
        "notebook": analysis_markdown(payload["summary"], payload["effects"], design),
    }
    for key, relative in OUTPUTS.items():
        path = output_root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(values[key])
    project_root = design_path.parents[2]
    manifest = {
        "_schema": "police_thief_research_manifest_v1",
        "operation_class": "LOCAL_SIMULATOR_EXPERIMENT",
        "design": _file_record(design_path, project_root),
        "record_count": payload["record_count"],
        "artifacts": {
            key: _bytes_record(relative, values[key]) for key, relative in OUTPUTS.items()
        },
        "source_files": _hash_files(project_root, SOURCE_FILES),
        "frozen_files": _hash_files(project_root, FROZEN_FILES),
        "matched_sensitive_values_retained": False,
    }
    manifest_path = output_root / "results/research/phase4d9_manifest.json"
    manifest_path.write_bytes(_json_bytes(manifest))
    return manifest


def _json_bytes(value: Any) -> bytes:
    """Serialize deterministic public evidence as sorted indented UTF-8 JSON."""
    return (json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n").encode()


def _bytes_record(path: Path, value: bytes) -> dict[str, Any]:
    """Describe one generated artifact without embedding its body."""
    return {
        "path": path.as_posix(),
        "bytes": len(value),
        "sha256": hashlib.sha256(value).hexdigest(),
    }


def _file_record(path: Path, root: Path) -> dict[str, Any]:
    """Describe one existing input file using a repository-relative path."""
    return _bytes_record(path.relative_to(root), path.read_bytes())


def _hash_files(root: Path, relative_paths: tuple[str, ...]) -> dict[str, str]:
    """Hash declared source inputs in deterministic path order."""
    return {
        relative: hashlib.sha256((root / relative).read_bytes()).hexdigest()
        for relative in relative_paths
    }
