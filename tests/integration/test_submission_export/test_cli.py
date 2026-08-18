"""Tests for the submission-export CLI entry point."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from tools.submission_export.cli import main

pytestmark = pytest.mark.integration


def _write_manifest(path: Path, manifest: dict) -> Path:
    manifest_file = path / "manifest.json"
    manifest_file.write_text(json.dumps(manifest), encoding="utf-8")
    return manifest_file


def test_plan_command_exits_0_on_valid_manifest(
    police_manifest: dict, repo_root: Path, tmp_path: Path
) -> None:
    mf = _write_manifest(tmp_path, police_manifest)
    rc = main(["--repo-root", str(repo_root), "plan", str(mf)])
    assert rc == 0


def test_export_command_exits_0_on_valid_manifest(
    police_manifest: dict, repo_root: Path, tmp_path: Path
) -> None:
    mf = _write_manifest(tmp_path, police_manifest)
    out_dir = tmp_path / "output"
    out_dir.mkdir()
    rc = main(["--repo-root", str(repo_root), "export", str(mf), str(out_dir)])
    assert rc == 0


def test_plan_exits_1_on_bad_schema(
    police_manifest: dict, repo_root: Path, tmp_path: Path
) -> None:
    bad = dict(police_manifest, schema="bad_schema_vX")
    mf = _write_manifest(tmp_path, bad)
    rc = main(["--repo-root", str(repo_root), "plan", str(mf)])
    assert rc == 1


def test_plan_exits_1_on_wrong_source_commit(
    police_manifest: dict, repo_root: Path, tmp_path: Path
) -> None:
    bad = dict(police_manifest, source_commit="0" * 40)
    mf = _write_manifest(tmp_path, bad)
    rc = main(["--repo-root", str(repo_root), "plan", str(mf)])
    assert rc == 1


def test_export_exits_1_on_non_empty_output_dir(
    police_manifest: dict, repo_root: Path, tmp_path: Path
) -> None:
    mf = _write_manifest(tmp_path, police_manifest)
    out_dir = tmp_path / "output"
    out_dir.mkdir()
    (out_dir / "existing.txt").write_text("not empty", encoding="utf-8")
    rc = main(["--repo-root", str(repo_root), "export", str(mf), str(out_dir)])
    assert rc == 1


def test_cli_exit_codes_are_deterministic(
    police_manifest: dict, repo_root: Path, tmp_path: Path
) -> None:
    mf = _write_manifest(tmp_path, police_manifest)
    first = main(["--repo-root", str(repo_root), "plan", str(mf)])
    second = main(["--repo-root", str(repo_root), "plan", str(mf)])
    assert first == second == 0


def test_plan_exits_1_on_missing_manifest_file(
    repo_root: Path, tmp_path: Path
) -> None:
    rc = main(["--repo-root", str(repo_root), "plan", str(tmp_path / "missing.json")])
    assert rc == 1
