"""Build and verify one role candidate through the guarded partner exporter."""

from __future__ import annotations

import json
from pathlib import Path

from tools.offline_ops.secrets.scanner import scan_path
from tools.submission_assembly.hashing import hash_tree
from tools.submission_assembly.policy import build_export_manifest, role_overlay
from tools.submission_export.exporter import export_to


def prepare_role(policy_path: Path, role: str, output: Path, repo_root: Path) -> dict[str, object]:
    """Create one candidate tree and deterministic evidence directory."""
    tree = output / "tree"
    evidence = output / "evidence"
    tree.mkdir(parents=True)
    evidence.mkdir()
    export_input = build_export_manifest(policy_path, role, repo_root)
    export_plan = export_to(export_input, tree, repo_root)
    (tree / "export_manifest.json").replace(evidence / "export_plan.json")
    _write_json(evidence / "export_input.json", export_input)
    overlay = role_overlay(policy_path, role)
    (tree / "README.md").write_bytes((repo_root / overlay).read_bytes())
    final_files, final_hash = hash_tree(tree)
    _require_only_readme_changed(export_plan, final_files)
    findings = scan_path(tree)
    if findings:
        categories = sorted({finding.category for finding in findings})
        raise ValueError(f"candidate secret scan failed by category: {categories!r}")
    candidate = {
        "schema": "role_candidate_manifest_v1",
        "role": role,
        "source_commit": export_input["source_commit"],
        "counterpart_repository_url": export_input["counterpart_repository_url"],
        "readme_overlay": overlay,
        "base_export_aggregate_hash": export_plan["aggregate_hash"],
        "candidate_aggregate_hash": final_hash,
        "file_count": len(final_files),
        "files": final_files,
        "secret_scan": "PASS",
        "external_operations_authorized": False,
    }
    _write_json(evidence / "candidate_manifest.json", candidate)
    return candidate


def _require_only_readme_changed(
    export_plan: dict[str, object], final_files: list[dict[str, str]]
) -> None:
    """Require the role overlay to be the export's only byte change."""
    original = {entry["path"]: entry["sha256"] for entry in export_plan["files"]}
    final = {entry["path"]: entry["sha256"] for entry in final_files}
    if original.keys() != final.keys():
        raise ValueError("candidate file set differs from the reviewed export plan")
    changed = sorted(path for path in original if original[path] != final[path])
    if changed != ["README.md"]:
        raise ValueError(f"candidate changed files outside the role README: {changed!r}")


def _write_json(path: Path, payload: dict[str, object]) -> None:
    """Write deterministic UTF-8 JSON with one trailing newline."""
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
