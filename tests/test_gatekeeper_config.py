"""Fail-closed configuration and lifecycle cases for the API gatekeeper."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from police_thief_lab.gatekeeper import ApiGatekeeper, RateLimitConfig, load_rate_limit_config
from police_thief_lab.gatekeeper_models import default_rate_limit_path


def _valid() -> dict:
    return {
        "schema_version": "1.0",
        "services": {
            "fastmcp": {
                "requests_per_minute": 60,
                "requests_per_hour": 600,
                "concurrent_max": 1,
                "queue_max": 4,
                "monitoring_max": 8,
            }
        },
    }


@pytest.mark.parametrize(
    ("value", "message"),
    [
        ([], "root fields mismatch"),
        ({"schema_version": "2.0", "services": {}}, "unsupported rate-limit schema"),
        ({"schema_version": "1.0", "services": {}}, "service is missing"),
    ],
)
def test_loader_rejects_wrong_root_schema_and_missing_service(
    tmp_path: Path, value: object, message: str
) -> None:
    path = tmp_path / "rate.json"
    path.write_text(json.dumps(value), encoding="utf-8")
    with pytest.raises(ValueError, match=message):
        load_rate_limit_config(path, "fastmcp")


def test_loader_rejects_unknown_missing_and_nonpositive_service_fields(tmp_path: Path) -> None:
    for name, mutate, message in (
        ("unknown", lambda row: row.update({"extra": 1}), "fields mismatch"),
        ("missing", lambda row: row.pop("queue_max"), "fields mismatch"),
        ("zero", lambda row: row.update({"queue_max": 0}), "must be a positive integer"),
        ("boolean", lambda row: row.update({"queue_max": True}), "must be a positive integer"),
    ):
        value = _valid()
        mutate(value["services"]["fastmcp"])
        path = tmp_path / f"{name}.json"
        path.write_text(json.dumps(value), encoding="utf-8")
        with pytest.raises(ValueError, match=message):
            load_rate_limit_config(path, "fastmcp")


def test_loader_rejects_malformed_or_unreadable_json(tmp_path: Path) -> None:
    malformed = tmp_path / "malformed.json"
    malformed.write_text("{", encoding="utf-8")
    for path in (malformed, tmp_path / "missing.json"):
        with pytest.raises(ValueError, match="invalid rate-limit config JSON"):
            load_rate_limit_config(path, "fastmcp")


def test_default_path_accepts_an_explicit_operator_environment_override(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    path = tmp_path / "operator-rate.json"
    monkeypatch.setenv("POLICE_THIEF_RATE_LIMITS_PATH", str(path))
    assert default_rate_limit_path() == path


def test_closed_gatekeeper_refuses_new_work_and_close_is_idempotent() -> None:
    config = RateLimitConfig("1.0", "fastmcp", 60, 600, 1, 4, 8)
    gate = ApiGatekeeper(config)
    gate.close()
    gate.close()
    with pytest.raises(RuntimeError, match="gatekeeper is closed"):
        gate.execute(lambda: None)
