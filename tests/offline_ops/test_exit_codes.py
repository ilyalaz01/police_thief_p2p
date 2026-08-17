"""Exit codes must match the Result contract table exactly."""

from __future__ import annotations

from tools.offline_ops.exit_codes import ExitCode


def test_exit_codes_match_the_documented_result_contract() -> None:
    assert ExitCode.SUCCESS == 0
    assert ExitCode.INVALID_INVOCATION == 2
    assert ExitCode.QUALITY_CHECK_FAILED == 3
    assert ExitCode.SECRET_SCAN_FAILED == 4
    assert ExitCode.MATCH_VALIDATION_FAILED == 5
    assert ExitCode.VALIDATOR_UNAVAILABLE == 6
    assert ExitCode.OUTPUT_WRITE_FAILED == 7


def test_exit_code_one_is_not_assigned() -> None:
    assert 1 not in {member.value for member in ExitCode}
