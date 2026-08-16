"""scan_artifact_directory must fail closed on every documented category."""

from __future__ import annotations

from pathlib import Path

import pytest

from tests.offline_ops.artifact_fixtures import write_valid_match_fixture
from tools.offline_ops.match_artifacts.hygiene import (
    MAX_FILE_COUNT,
    scan_artifact_directory,
)


def _categories(root: Path) -> set[str]:
    return {finding.category for finding in scan_artifact_directory(root)}


def test_missing_directory_raises_file_not_found(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        scan_artifact_directory(tmp_path / "does-not-exist")


def test_a_valid_fixture_has_no_findings(tmp_path: Path) -> None:
    write_valid_match_fixture(tmp_path)
    assert scan_artifact_directory(tmp_path) == []


def test_a_nested_directory_is_unexpected(tmp_path: Path) -> None:
    (tmp_path / "archive").mkdir()
    assert "unexpected_file" in _categories(tmp_path)


def test_a_non_matching_filename_is_unexpected(tmp_path: Path) -> None:
    (tmp_path / "notes.txt").write_text("hello", encoding="utf-8")
    assert "unexpected_file" in _categories(tmp_path)


def test_an_oversized_file_is_detected(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("tools.offline_ops.match_artifacts.hygiene.MAX_ARTIFACT_FILE_BYTES", 4)
    (tmp_path / "declaration_x.json").write_text("way too big", encoding="utf-8")
    assert "oversized_file" in _categories(tmp_path)


def test_total_size_cap_is_enforced(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("tools.offline_ops.match_artifacts.hygiene.MAX_TOTAL_BYTES", 3)
    (tmp_path / "declaration_x.json").write_text("{}", encoding="utf-8")
    (tmp_path / "result_x.json").write_text("{}", encoding="utf-8")
    assert "oversized_total" in _categories(tmp_path)


def test_too_many_files_is_detected(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("tools.offline_ops.match_artifacts.hygiene.MAX_FILE_COUNT", 2)
    for i in range(3):
        (tmp_path / f"config_x_g0{i}.json").write_text("{}", encoding="utf-8")
    findings = scan_artifact_directory(tmp_path)
    assert [f.category for f in findings] == ["too_many_files"]


def test_file_count_at_the_cap_is_not_flagged(tmp_path: Path) -> None:
    write_valid_match_fixture(tmp_path)
    assert len(list(tmp_path.iterdir())) <= MAX_FILE_COUNT


def test_symlink_is_detected(tmp_path: Path) -> None:
    outside = tmp_path.parent / "hygiene_outside.json"
    outside.write_text("{}", encoding="utf-8")
    root = tmp_path / "root"
    root.mkdir()
    link = root / "declaration_x.json"
    try:
        link.symlink_to(outside)
    except OSError:
        pytest.skip("symlink creation requires elevated privilege on this platform")
    try:
        assert "symlink" in _categories(root)
    finally:
        outside.unlink(missing_ok=True)
