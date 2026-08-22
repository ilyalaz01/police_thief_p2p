"""Versioned, operator-supplied configuration for official result reporting."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "reporting-1.0"
_REQUIRED = (
    "schema_version", "league_recipient", "sender_address", "subject_template",
    "attachment_name_template", "max_sends_per_game", "retry_attempts",
    "initial_backoff_seconds", "max_backoff_seconds",
)


def _address(value: Any, field: str) -> str:
    """Accept only a simple non-empty single address without display name."""
    if not isinstance(value, str) or value.count("@") != 1 or any(c.isspace() for c in value):
        raise ValueError(f"reporting {field} must be one plain e-mail address")
    local, _, domain = value.partition("@")
    if not local or "." not in domain:
        raise ValueError(f"reporting {field} must be one plain e-mail address")
    return value


def _positive(value: Any, field: str) -> float:
    """Accept only a positive, non-boolean number."""
    if isinstance(value, bool) or not isinstance(value, int | float) or value <= 0:
        raise ValueError(f"reporting {field} must be a positive number")
    return value


@dataclass(frozen=True, slots=True)
class ReportingConfig:
    """Exact reporting boundary values; no credential or token is ever stored here."""

    league_recipient: str
    sender_address: str
    subject_template: str
    attachment_name_template: str
    max_sends_per_game: int
    retry_attempts: int
    initial_backoff_seconds: float
    max_backoff_seconds: float

    def __post_init__(self) -> None:
        """Reject an incomplete or physically invalid reporting boundary."""
        _address(self.league_recipient, "league_recipient")
        _address(self.sender_address, "sender_address")
        for field in ("subject_template", "attachment_name_template"):
            value = getattr(self, field)
            if not isinstance(value, str) or "{game_id}" not in value:
                raise ValueError(f"reporting {field} must contain {{game_id}}")
        for field in ("max_sends_per_game", "retry_attempts"):
            value = getattr(self, field)
            if isinstance(value, bool) or not isinstance(value, int) or value < 1:
                raise ValueError(f"reporting {field} must be a positive integer")
        _positive(self.initial_backoff_seconds, "initial_backoff_seconds")
        _positive(self.max_backoff_seconds, "max_backoff_seconds")
        if self.max_backoff_seconds < self.initial_backoff_seconds:
            raise ValueError("reporting max_backoff_seconds is below initial_backoff_seconds")


def load_reporting_config(path: Path) -> ReportingConfig:
    """Load one operator reporting file, refusing an unknown schema or missing value."""
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError("reporting configuration must be one JSON object")
    missing = [name for name in _REQUIRED if raw.get(name) is None]
    if missing:
        raise ValueError(f"reporting configuration is missing values: {sorted(missing)}")
    if raw["schema_version"] != SCHEMA_VERSION:
        raise ValueError(
            f"reporting schema {raw['schema_version']!r} is not the supported {SCHEMA_VERSION!r}"
        )
    return ReportingConfig(
        league_recipient=raw["league_recipient"],
        sender_address=raw["sender_address"],
        subject_template=raw["subject_template"],
        attachment_name_template=raw["attachment_name_template"],
        max_sends_per_game=raw["max_sends_per_game"],
        retry_attempts=raw["retry_attempts"],
        initial_backoff_seconds=raw["initial_backoff_seconds"],
        max_backoff_seconds=raw["max_backoff_seconds"],
    )
