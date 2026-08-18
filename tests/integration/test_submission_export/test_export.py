"""Tests for the export operation."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from tools.submission_export.exporter import export_to

pytestmark = pytest.mark.integration


def test_export_to_empty_dir_succeeds(
    police_manifest: dict, repo_root: Path, tmp_path: Path
) -> None:
    result = export_to(police_manifest, tmp_path, repo_root)
    assert result["schema"] == "submission_export_plan_v1"


def test_exported_files_exist_in_output(
    police_manifest: dict, repo_root: Path, tmp_path: Path
) -> None:
    export_to(police_manifest, tmp_path, repo_root)
    for posix_path in police_manifest["include"]:
        assert (tmp_path / posix_path).exists(), f"missing: {posix_path}"


def test_exported_bytes_equal_source_bytes(
    police_manifest: dict, repo_root: Path, tmp_path: Path
) -> None:
    export_to(police_manifest, tmp_path, repo_root)
    for posix_path in police_manifest["include"]:
        src = (repo_root / posix_path).read_bytes()
        dst = (tmp_path / posix_path).read_bytes()
        assert src == dst, f"byte mismatch: {posix_path}"


def test_exported_per_file_hashes_match_plan(
    police_manifest: dict, repo_root: Path, tmp_path: Path
) -> None:
    result = export_to(police_manifest, tmp_path, repo_root)
    for entry in result["files"]:
        data = (tmp_path / entry["path"]).read_bytes()
        assert hashlib.sha256(data).hexdigest() == entry["sha256"]


def test_export_manifest_json_written_to_output(
    police_manifest: dict, repo_root: Path, tmp_path: Path
) -> None:
    export_to(police_manifest, tmp_path, repo_root)
    manifest_file = tmp_path / "export_manifest.json"
    assert manifest_file.exists()
    loaded = json.loads(manifest_file.read_text(encoding="utf-8"))
    assert loaded["schema"] == "submission_export_plan_v1"
    assert loaded["role"] == "police"


def test_export_refuses_non_empty_output_directory(
    police_manifest: dict, repo_root: Path, tmp_path: Path
) -> None:
    (tmp_path / "existing.txt").write_text("not empty", encoding="utf-8")
    with pytest.raises(ValueError, match="non-empty|empty"):
        export_to(police_manifest, tmp_path, repo_root)


def test_export_refuses_nonexistent_output_directory(
    police_manifest: dict, repo_root: Path, tmp_path: Path
) -> None:
    missing = tmp_path / "does_not_exist"
    with pytest.raises(FileNotFoundError):
        export_to(police_manifest, missing, repo_root)


def test_export_rule50_layout_present(
    police_manifest: dict, repo_root: Path, tmp_path: Path
) -> None:
    export_to(police_manifest, tmp_path, repo_root)
    assert (tmp_path / "README.md").exists()
    assert (tmp_path / "docs" / "PRD.md").exists()
    assert (tmp_path / "docs" / "PLAN.md").exists()
    assert (tmp_path / "docs" / "TODO.md").exists()
    assert any((tmp_path / "config").iterdir())
