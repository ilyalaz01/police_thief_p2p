"""Operator Gmail credential file: least privilege, never logged, never committed."""

from __future__ import annotations

import json
import os
import stat
from dataclasses import dataclass
from pathlib import Path
from typing import Any

SEND_SCOPE = "https://www.googleapis.com/auth/gmail.send"
TOKEN_URI = "https://oauth2.googleapis.com/token"
SEND_URI = "https://gmail.googleapis.com/gmail/v1/users/me/messages/send"
_REQUIRED = ("client_id", "client_secret", "refresh_token")


@dataclass(frozen=True, slots=True)
class GmailCredentials:
    """The three operator values needed to obtain one short-lived send-only token."""

    client_id: str
    client_secret: str
    refresh_token: str
    token_uri: str = TOKEN_URI
    send_uri: str = SEND_URI

    def __post_init__(self) -> None:
        """Refuse an empty or placeholder credential before any network call."""
        for field in _REQUIRED:
            value = getattr(self, field)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"gmail credential {field} is empty")
            if value.startswith("REPLACE_WITH"):
                raise ValueError(f"gmail credential {field} is still the placeholder")
        for field in ("token_uri", "send_uri"):
            if not getattr(self, field).startswith("https://"):
                raise ValueError(f"gmail {field} must be an HTTPS endpoint")

    def redacted(self) -> dict[str, Any]:
        """Return an operator-readable summary that reveals no secret value."""
        return {
            "client_id_suffix": self.client_id[-12:],
            "client_secret": "<redacted>",
            "refresh_token": "<redacted>",
            "token_uri": self.token_uri,
            "send_uri": self.send_uri,
            "scope": SEND_SCOPE,
        }


def load_gmail_credentials(path: Path) -> GmailCredentials:
    """Read one local credential file without echoing any value it contains."""
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError("gmail credential file must be one JSON object")
    missing = [name for name in _REQUIRED if raw.get(name) is None]
    if missing:
        raise ValueError(f"gmail credential file is missing values: {sorted(missing)}")
    return GmailCredentials(
        client_id=raw["client_id"],
        client_secret=raw["client_secret"],
        refresh_token=raw["refresh_token"],
        token_uri=raw.get("token_uri", TOKEN_URI),
        send_uri=raw.get("send_uri", SEND_URI),
    )


def save_gmail_credentials(path: Path, credentials: GmailCredentials) -> Path:
    """Write the credential file with owner-only permissions where the OS supports it."""
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        json.dumps(
            {
                "client_id": credentials.client_id,
                "client_secret": credentials.client_secret,
                "refresh_token": credentials.refresh_token,
                "token_uri": credentials.token_uri,
                "send_uri": credentials.send_uri,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    with contextlib_suppress():
        os.chmod(target, stat.S_IRUSR | stat.S_IWUSR)
    return target


def contextlib_suppress():
    """Return a suppressing context manager for platforms without POSIX permissions."""
    from contextlib import suppress

    return suppress(OSError, NotImplementedError)
