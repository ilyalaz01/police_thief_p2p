"""build_manifest/render_markdown/write_package must stay redacted and atomic."""

from __future__ import annotations

import hashlib
from pathlib import Path

import pytest

from tools.offline_ops.match_artifacts.packager import (
    build_manifest,
    render_markdown,
    write_package,
)
from tools.offline_ops.models import CheckResult, CheckStatus, GateReport


def _validation(exit_code: int = 0) -> GateReport:
    check = CheckResult(
        check_id="artifact_hygiene",
        status=CheckStatus.PASS,
        explanation="no findings",
        duration_seconds=0.01,
        exit_code=0,
    )
    return GateReport(command="validate-match", checks=(check,), exit_code=exit_code)


def test_manifest_reports_filename_bytes_and_sha256(tmp_path: Path) -> None:
    artifact = tmp_path / "declaration_x.json"
    artifact.write_text('{"a": 1}', encoding="utf-8")

    manifest = build_manifest([artifact], _validation())

    assert manifest["files"] == [
        {
            "filename": "declaration_x.json",
            "byte_length": 8,
            "sha256": hashlib.sha256(b'{"a": 1}').hexdigest(),
        }
    ]
    assert manifest["checks"][0]["check_id"] == "artifact_hygiene"
    assert manifest["overall_exit_code"] == 0


def test_manifest_never_contains_file_contents(tmp_path: Path) -> None:
    secret_like = "commit_value_should_never_appear_in_manifest"
    artifact = tmp_path / "log_x_g01.json"
    artifact.write_text(f'{{"records": ["{secret_like}"]}}', encoding="utf-8")

    manifest = build_manifest([artifact], _validation())

    assert secret_like not in str(manifest)


def test_markdown_report_mirrors_the_manifest(tmp_path: Path) -> None:
    artifact = tmp_path / "result_x.json"
    artifact.write_text("{}", encoding="utf-8")
    manifest = build_manifest([artifact], _validation())

    markdown = render_markdown(manifest)

    assert "result_x.json" in markdown
    assert "artifact_hygiene" in markdown
    assert "Overall exit code: 0" in markdown


def test_write_package_is_atomic_and_byte_identical(tmp_path: Path) -> None:
    source = tmp_path / "source"
    source.mkdir()
    artifact = source / "declaration_x.json"
    artifact.write_bytes(b'{"a": 1}')
    output = tmp_path / "package"
    manifest = build_manifest([artifact], _validation())
    markdown = render_markdown(manifest)

    write_package([artifact], manifest, markdown, output)

    assert (output / "declaration_x.json").read_bytes() == b'{"a": 1}'
    assert (output / "package_manifest.json").exists()
    assert (output / "package_report.md").exists()
    assert not any(p.name.startswith(".package.partial-") for p in tmp_path.iterdir())


def test_write_package_never_leaves_a_partial_directory_on_failure(tmp_path: Path) -> None:
    source = tmp_path / "source"
    source.mkdir()
    missing_artifact = source / "declaration_x.json"  # never written: read_bytes() will raise
    output = tmp_path / "package"
    manifest = build_manifest([], _validation())

    with pytest.raises(OSError):
        write_package([missing_artifact], manifest, "report", output)

    assert not output.exists()
    assert list(tmp_path.iterdir()) == [source]
