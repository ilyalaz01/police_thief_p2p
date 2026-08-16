"""package-match must validate first and never overwrite an existing output."""

from __future__ import annotations

import json
from pathlib import Path

from tests.offline_ops.artifact_fixtures import write_valid_match_fixture
from tools.offline_ops.commands import package_match
from tools.offline_ops.exit_codes import ExitCode
from tools.offline_ops.models import CheckStatus


def test_a_valid_match_is_packaged_end_to_end(tmp_path: Path) -> None:
    source = tmp_path / "source"
    write_valid_match_fixture(source)
    output = tmp_path / "package"

    report = package_match.run(source, output)

    assert report.exit_code == ExitCode.SUCCESS
    package_files = {p.name for p in output.iterdir()}
    assert package_files == {
        "declaration_alpha-vs-bravo.json",
        "config_alpha-vs-bravo_g01.json",
        "log_alpha-vs-bravo_g01.json",
        "result_alpha-vs-bravo.json",
        "package_manifest.json",
        "package_report.md",
    }
    manifest = json.loads((output / "package_manifest.json").read_text(encoding="utf-8"))
    assert len(manifest["files"]) == 4


def test_invalid_source_is_never_packaged(tmp_path: Path) -> None:
    source = tmp_path / "source"
    source.mkdir()  # empty: fails the composed checker
    output = tmp_path / "package"

    report = package_match.run(source, output)

    assert report.exit_code != ExitCode.SUCCESS
    assert not output.exists()


def test_existing_output_is_never_overwritten(tmp_path: Path) -> None:
    source = tmp_path / "source"
    write_valid_match_fixture(source)
    output = tmp_path / "package"
    output.mkdir()
    (output / "sentinel.txt").write_text("do not touch", encoding="utf-8")

    report = package_match.run(source, output)

    assert report.exit_code == ExitCode.OUTPUT_WRITE_FAILED
    assert report.checks[-1].check_id == "package_write"
    assert report.checks[-1].status == CheckStatus.FAIL
    assert (output / "sentinel.txt").read_text(encoding="utf-8") == "do not touch"


def test_a_nonce_in_the_log_artifact_stays_confined_and_out_of_reports(tmp_path: Path) -> None:
    """A revealed commit-reveal nonce legitimately lives in a terminal-audit
    log artifact (RULES_AND_INTEROP_BASELINE.md ~5). It must stay only in
    that unchanged, byte-identical packaged file, never in the generated
    manifest/report, and must not itself trip the secret scanner.
    """
    source = tmp_path / "source"
    write_valid_match_fixture(source)
    log_file = next(source.glob("log_*.json"))
    revealed_nonce = "b3f1c2a9-revealed-audit-nonce-should-stay-confined"
    doc = json.loads(log_file.read_text(encoding="utf-8"))
    doc["records"] = [{"step": 1, "nonce": revealed_nonce}]
    log_file.write_text(json.dumps(doc, indent=2), encoding="utf-8")
    output = tmp_path / "package"

    report = package_match.run(source, output)

    assert report.exit_code == ExitCode.SUCCESS
    assert revealed_nonce in (output / log_file.name).read_text(encoding="utf-8")
    assert revealed_nonce not in (output / "package_manifest.json").read_text(encoding="utf-8")
    assert revealed_nonce not in (output / "package_report.md").read_text(encoding="utf-8")


def test_packaged_artifact_bytes_match_the_source_exactly(tmp_path: Path) -> None:
    source = tmp_path / "source"
    write_valid_match_fixture(source)
    output = tmp_path / "package"

    package_match.run(source, output)

    for source_file in source.iterdir():
        assert (output / source_file.name).read_bytes() == source_file.read_bytes()
