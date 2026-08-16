"""Versioned operational configuration and secret-boundary requirements."""

import json
import sys
import tomllib
from pathlib import Path

import pytest
from interop_test_support import profile

from police_thief_lab import __version__
from police_thief_lab.configuration import (
    CONFIG_SCHEMA_VERSION,
    load_operational_config,
    scan_configuration_secrets,
)

ROOT = Path(__file__).parents[1]
TRACKED_CONFIG = ROOT / "config/operational.self-test.v1.json"


def _write_config(tmp_path: Path, **changes: object) -> Path:
    value = {
        "schema_version": "1.0",
        "package_version": "1.0.0",
        "operation_mode": "self_test",
        "secret_source": "environment_only",
        "retain_sensitive_values": False,
    }
    value.update(changes)
    path = tmp_path / "operational.json"
    path.write_text(json.dumps(value), encoding="utf-8")
    return path


def test_tracked_config_and_project_versions_are_coherent() -> None:
    loaded = load_operational_config(TRACKED_CONFIG)
    project = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    assert CONFIG_SCHEMA_VERSION == "1.0"
    assert loaded.schema_version == CONFIG_SCHEMA_VERSION
    assert loaded.package_version == __version__ == project["project"]["version"]
    assert loaded.operation_mode == "self_test"
    assert loaded.secret_source == "environment_only"
    assert loaded.retain_sensitive_values is False


@pytest.mark.parametrize(
    ("changes", "message"),
    [
        ({"schema_version": "2.0"}, "unsupported operational config schema: 2.0"),
        ({"package_version": "9.0.0"}, "operational config package version mismatch"),
        ({"operation_mode": "counted"}, "unsupported operation mode: counted"),
        ({"secret_source": "json"}, "operational secrets must come from the environment"),
        ({"retain_sensitive_values": True}, "sensitive-value retention must remain disabled"),
    ],
)
def test_loader_rejects_incompatible_or_unsafe_values(
    tmp_path: Path,
    changes: dict[str, object],
    message: str,
) -> None:
    with pytest.raises(ValueError, match=f"^{message}$"):
        load_operational_config(_write_config(tmp_path, **changes))


def test_loader_rejects_missing_and_unknown_fields(tmp_path: Path) -> None:
    missing = json.loads(_write_config(tmp_path).read_text())
    missing.pop("operation_mode")
    missing_path = tmp_path / "missing.json"
    missing_path.write_text(json.dumps(missing))
    with pytest.raises(ValueError, match="operational config fields mismatch"):
        load_operational_config(missing_path)
    with pytest.raises(ValueError, match="operational config fields mismatch"):
        load_operational_config(_write_config(tmp_path, api_token="not-allowed"))


def test_loading_operational_config_cannot_change_match_profile_bytes() -> None:
    shared = profile()
    before = (shared.bytes(), shared.sha256, shared.reference_terms())
    load_operational_config(TRACKED_CONFIG)
    assert (shared.bytes(), shared.sha256, shared.reference_terms()) == before


def test_secret_scan_reports_location_and_category_without_value(tmp_path: Path) -> None:
    unsafe = tmp_path / ".env"
    unsafe.write_text("API_TOKEN=synthetic-sensitive-value\n", encoding="utf-8")
    findings = scan_configuration_secrets((unsafe,))
    assert findings == (f"{unsafe}:1:credential_assignment",)
    assert "synthetic-sensitive-value" not in json.dumps(findings)


def test_tracked_config_and_environment_example_pass_secret_scan() -> None:
    assert scan_configuration_secrets((TRACKED_CONFIG, ROOT / ".env-example")) == ()


def test_invalid_operational_config_stops_cli_before_peer_side_effects(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    from police_thief_lab import peer_cli
    from police_thief_lab.sdk import transport as sdk_transport

    invalid = _write_config(tmp_path, schema_version="2.0")
    monkeypatch.setattr(
        sdk_transport,
        "_run_peer",
        lambda *_args: (_ for _ in ()).throw(AssertionError("peer side effect started")),
    )
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "peer_cli",
            "--role",
            "police",
            "--operational-config",
            str(invalid),
            "--profile",
            str(tmp_path / "unused-profile.json"),
            "--port",
            "8801",
            "--opponent-url",
            "http://127.0.0.1:8802/mcp",
            "--artifacts",
            str(tmp_path / "artifacts"),
            "--output",
            str(tmp_path / "result.json"),
        ],
    )
    with pytest.raises(ValueError, match="unsupported operational config schema"):
        peer_cli.main()


def test_environment_selected_mode_mismatch_stops_cli_before_peer_side_effects(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    from police_thief_lab import peer_cli
    from police_thief_lab.sdk import transport as sdk_transport

    monkeypatch.setenv("POLICE_THIEF_CONFIG_PATH", str(TRACKED_CONFIG))
    monkeypatch.setattr(
        sdk_transport,
        "_run_peer",
        lambda *_args: (_ for _ in ()).throw(AssertionError("peer side effect started")),
    )
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "peer_cli",
            "--role",
            "police",
            "--real-team",
            "--profile",
            str(tmp_path / "unused-profile.json"),
            "--port",
            "8801",
            "--opponent-url",
            "http://127.0.0.1:8802/mcp",
            "--artifacts",
            str(tmp_path / "artifacts"),
            "--output",
            str(tmp_path / "result.json"),
        ],
    )
    with pytest.raises(ValueError, match="config mode does not match"):
        peer_cli.main()
