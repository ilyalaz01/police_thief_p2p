"""Provider-neutral public transport configuration and safe diagnostics."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from urllib.parse import SplitResult, urlsplit, urlunsplit


def validate_mcp_url(value: str, *, public: bool = False) -> str:
    parsed = urlsplit(value)
    allowed = {"https"} if public else {"http", "https"}
    if parsed.scheme not in allowed or not parsed.hostname:
        expected = "HTTPS" if public else "HTTP(S)"
        raise ValueError(f"MCP URL must be an absolute {expected} URL")
    if parsed.username or parsed.password or parsed.query or parsed.fragment:
        raise ValueError("MCP URL must not contain credentials, query, or fragment")
    if parsed.path != "/mcp":
        raise ValueError("MCP URL path must be exactly /mcp")
    try:
        port = parsed.port
    except ValueError as exc:
        raise ValueError("MCP URL has an invalid port") from exc
    if port is not None and not 1 <= port <= 65535:
        raise ValueError("MCP URL port must be between 1 and 65535")
    return value


def redact_url(value: str) -> str:
    """Remove URL credentials/query material while retaining routing context."""
    parsed = urlsplit(value)
    host = parsed.hostname or "invalid"
    if parsed.port:
        host = f"{host}:{parsed.port}"
    return urlunsplit(SplitResult(parsed.scheme, host, parsed.path, "", ""))


def redact_secrets(value: Any) -> Any:
    """Recursively redact common credential and commit-reveal secret fields."""
    if isinstance(value, dict):
        return {
            key: (
                "<redacted>"
                if any(
                    word in key.lower()
                    for word in (
                        "nonce", "token", "secret", "password", "authorization", "oauth"
                    )
                )
                else redact_secrets(item)
            )
            for key, item in value.items()
        }
    if isinstance(value, list):
        return [redact_secrets(item) for item in value]
    return value


@dataclass(frozen=True, slots=True)
class EndpointConfig:
    bind_host: str
    local_port: int
    advertised_url: str
    opponent_url: str
    connect_timeout: float
    turn_timeout: float
    retry_interval: float
    retry_count: int
    audit_timeout: float
    public: bool = False

    def __post_init__(self) -> None:
        if not self.bind_host.strip():
            raise ValueError("local bind host is required")
        if not 1 <= self.local_port <= 65535:
            raise ValueError("local port must be between 1 and 65535")
        validate_mcp_url(self.advertised_url, public=self.public)
        validate_mcp_url(self.opponent_url, public=self.public)
        if min(self.connect_timeout, self.turn_timeout, self.audit_timeout) <= 0:
            raise ValueError("timeouts must be positive")
        if self.retry_interval < 0 or self.retry_count < 0:
            raise ValueError("retry interval and count must be non-negative")
