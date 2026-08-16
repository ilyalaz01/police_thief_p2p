"""Detection patterns and prune lists for the scan-secrets command.

Every pattern here only classifies a finding's *category*; matched text is
never retained or reported, per the workstream's "never print or commit a
detected value" requirement.
"""

from __future__ import annotations

import re

#: Directory names pruned entirely from every scan. ``external`` is the
#: pinned, independently-versioned third-party conformance-kit submodule,
#: which this workstream must not audit or reinterpret (see
#: ``RELEASE_ENGINEERING_WORKSTREAM.md`` module boundary).
SKIP_DIRECTORY_NAMES: frozenset[str] = frozenset(
    {
        ".git",
        ".venv",
        "venv",
        "__pycache__",
        ".pytest_cache",
        ".mypy_cache",
        ".ruff_cache",
        "node_modules",
        "external",
    }
)

#: Top-level relative directory whose files are exempt from the
#: non-artifact-nonce check only: it is this project's own sanctioned
#: location for committed interoperability golden vectors and fixtures,
#: which legitimately contain synthetic nonce values.
NONCE_EXEMPT_TOP_LEVEL_DIR = "interop"

CACHE_AND_TEMP_NAME_PATTERNS: tuple[str, ...] = (
    "*.pyc",
    "*.pyo",
    "*.tmp",
    "*.bak",
    "*.swp",
    "*.orig",
    ".DS_Store",
    "Thumbs.db",
)

TUNNEL_CONFIG_NAME_PATTERNS: tuple[str, ...] = (
    "ngrok.yml",
    "ngrok.yaml",
    "cloudflared.yml",
    "frpc.ini",
    "frps.ini",
)

_CREDENTIAL_PATTERNS: dict[str, re.Pattern[str]] = {
    "private_key": re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    "aws_access_key": re.compile(r"AKIA[0-9A-Z]{16}"),
    "github_token": re.compile(r"gh[pousr]_[A-Za-z0-9]{20,}"),
    "slack_token": re.compile(r"xox[baprs]-[A-Za-z0-9-]{10,}"),
    "generic_secret_assignment": re.compile(
        r"(?i)\b(api[_-]?key|secret[_-]?key|access[_-]?token|password)\b"
        r"\s*[:=]\s*['\"][^'\"\s]{8,}['\"]"
    ),
    "authorization_header": re.compile(r"(?i)authorization\s*:\s*(bearer|basic)\s+\S+"),
    "jwt": re.compile(r"\beyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\b"),
    "tunnel_url": re.compile(
        r"(?i)\b[a-z0-9-]+\.(ngrok(-free)?\.app|ngrok\.io|trycloudflare\.com|loca\.lt)\b"
    ),
}

NONCE_KEY_PATTERN = re.compile(r'"nonce"\s*:')

ARTIFACT_NAME_PREFIXES: tuple[str, ...] = ("declaration_", "config_", "log_", "result_")


def credential_patterns() -> dict[str, re.Pattern[str]]:
    """Return the credential/token/tunnel content detection patterns."""
    return _CREDENTIAL_PATTERNS
