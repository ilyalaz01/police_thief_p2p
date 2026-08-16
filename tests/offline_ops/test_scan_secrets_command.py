"""scan-secrets command must map scanner findings to the exit-code contract."""

from __future__ import annotations

from pathlib import Path

from tools.offline_ops.commands import scan_secrets
from tools.offline_ops.exit_codes import ExitCode
from tools.offline_ops.models import CheckStatus


def test_missing_path_is_validator_unavailable(tmp_path: Path) -> None:
    report = scan_secrets.run(tmp_path / "does-not-exist")
    assert report.exit_code == ExitCode.VALIDATOR_UNAVAILABLE
    assert report.checks[0].status == CheckStatus.UNAVAILABLE


def test_clean_directory_passes(tmp_path: Path) -> None:
    report = scan_secrets.run(tmp_path)
    assert report.exit_code == ExitCode.SUCCESS
    assert report.checks[0].status == CheckStatus.PASS


def test_a_finding_fails_closed_and_never_echoes_the_matched_value(tmp_path: Path) -> None:
    secret_value = "AKIAAAAAAAAAAAAAAAAA"
    (tmp_path / "leak.txt").write_text(secret_value, encoding="utf-8")

    report = scan_secrets.run(tmp_path)

    assert report.exit_code == ExitCode.SECRET_SCAN_FAILED
    assert report.checks[0].status == CheckStatus.FAIL
    assert secret_value not in report.checks[0].explanation
