"""Strict versioned startup configuration outside negotiated game-profile bytes."""

from __future__ import annotations

import json
import re
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

CONFIG_SCHEMA_VERSION = "1.0"
_FIELDS = frozenset(
    {
        "schema_version",
        "package_version",
        "operation_mode",
        "secret_source",
        "retain_sensitive_values",
    }
)
_MODES = frozenset({"offline", "self_test", "real_team"})
_ENV_CREDENTIAL = re.compile(
    r"^\s*[A-Za-z_][A-Za-z0-9_]*(?:TOKEN|SECRET|PASSWORD|CREDENTIAL|API_KEY|OAUTH)"
    r"[A-Za-z0-9_]*\s*=\s*(?P<value>.+?)\s*$",
    re.IGNORECASE,
)
_JSON_CREDENTIAL = re.compile(
    r'^\s*"(?P<key>[^"]*(?:token|secret|password|credential|api_key|oauth)[^"]*)"'
    r"\s*:\s*(?P<value>.+?)\s*,?\s*$",
    re.IGNORECASE,
)


@dataclass(frozen=True, slots=True)
class OperationalConfig:
    """Validated startup classification and secret-retention boundary."""

    schema_version: str
    package_version: str
    operation_mode: str
    secret_source: str
    retain_sensitive_values: bool


def _require_string(value: Any, field: str) -> str:
    """Compute the internal require string step used by module."""
    if not isinstance(value, str) or not value:
        raise ValueError(f"operational config {field} must be a non-empty string")
    return value


def load_operational_config(path: Path) -> OperationalConfig:
    """Load and validate startup metadata before any peer side effect."""
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ValueError("invalid operational config JSON") from exc
    if not isinstance(raw, dict) or frozenset(raw) != _FIELDS:
        raise ValueError("operational config fields mismatch")
    schema_version = _require_string(raw["schema_version"], "schema_version")
    if schema_version != CONFIG_SCHEMA_VERSION:
        raise ValueError(f"unsupported operational config schema: {schema_version}")
    package_version = _require_string(raw["package_version"], "package_version")
    from . import __version__

    if package_version != __version__:
        raise ValueError("operational config package version mismatch")
    operation_mode = _require_string(raw["operation_mode"], "operation_mode")
    if operation_mode not in _MODES:
        raise ValueError(f"unsupported operation mode: {operation_mode}")
    secret_source = _require_string(raw["secret_source"], "secret_source")
    if secret_source != "environment_only":
        raise ValueError("operational secrets must come from the environment")
    if raw["retain_sensitive_values"] is not False:
        raise ValueError("sensitive-value retention must remain disabled")
    return OperationalConfig(
        schema_version,
        package_version,
        operation_mode,
        secret_source,
        False,
    )


def _credential_assignment(line: str) -> bool:
    """Compute the internal credential assignment step used by module."""
    env_match = _ENV_CREDENTIAL.match(line)
    if env_match and env_match.group("value").strip(' "\''):
        return True
    json_match = _JSON_CREDENTIAL.match(line)
    if not json_match or json_match.group("key").lower() == "secret_source":
        return False
    value = json_match.group("value").rstrip(",").strip()
    return value not in {'""', "null", "false", "0"}


def scan_configuration_secrets(paths: Iterable[Path]) -> tuple[str, ...]:
    """Return sanitized path/line/categories without retaining matched values."""
    findings = []
    for path in paths:
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            lowered = line.lower()
            category = None
            if "-----begin " in lowered and "private key-----" in lowered:
                category = "private_key"
            elif re.match(r"^\s*authorization\s*:\s*\S+", line, re.IGNORECASE):
                category = "authorization_header"
            elif _credential_assignment(line):
                category = "credential_assignment"
            if category:
                findings.append(f"{path}:{number}:{category}")
    return tuple(findings)
