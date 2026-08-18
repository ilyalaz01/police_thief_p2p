"""Final-series team identity and exact per-sub-game Git provenance gates."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any
from urllib.parse import urlsplit

from ..interop.runtime_models import UNRESOLVED_GIT_COMMIT


def _nonempty(value: Any, field: str) -> str:
    """Return a nonblank string while preserving its exact value."""
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"declaration {field} must be a non-empty string")
    return value


def validate_group_id(value: Any) -> str:
    """Enforce the official exact eight-character, no-whitespace group ID."""
    group_id = _nonempty(value, "group_id")
    if len(group_id) != 8 or any(character.isspace() for character in group_id):
        raise ValueError("declaration group_id must be exactly 8 characters without spaces")
    return group_id


def _github_url(value: Any, field: str) -> str:
    """Require an explicit HTTPS GitHub repository URL without contacting it."""
    url = _nonempty(value, field)
    parsed = urlsplit(url)
    if (
        parsed.scheme != "https" or parsed.netloc.lower() != "github.com"
        or not parsed.path.strip("/") or parsed.username or parsed.password
        or parsed.query or parsed.fragment
    ):
        raise ValueError(f"declaration {field} must be an HTTPS GitHub repository URL")
    return url


def _mcp_url(value: Any, field: str) -> str:
    """Require a public-shaped HTTPS MCP identity without making a request."""
    url = _nonempty(value, field)
    parsed = urlsplit(url)
    if (
        parsed.scheme != "https" or not parsed.netloc or parsed.path.rstrip("/") != "/mcp"
        or parsed.username or parsed.password or parsed.query or parsed.fragment
    ):
        raise ValueError(f"declaration {field} must be an HTTPS /mcp URL")
    return url


@dataclass(frozen=True, slots=True)
class HardwareIdentity:
    """Official declaration hardware fields supplied by a team operator."""

    cpu_type: str
    cpu_freq_mhz: float
    cpu_cores: int
    ram_gb: float
    gpu_model: str
    vram_gb: float

    def __post_init__(self) -> None:
        """Reject empty or physically invalid operator-supplied hardware values."""
        _nonempty(self.cpu_type, "cpu_type")
        _nonempty(self.gpu_model, "gpu_model")
        numbers = (self.cpu_freq_mhz, self.ram_gb, self.vram_gb)
        if any(isinstance(value, bool) or not isinstance(value, int | float) for value in numbers):
            raise ValueError("declaration hardware numbers must be numeric")
        if self.cpu_freq_mhz <= 0 or self.ram_gb <= 0 or self.vram_gb < 0:
            raise ValueError("declaration hardware values are out of range")
        if (
            isinstance(self.cpu_cores, bool)
            or not isinstance(self.cpu_cores, int)
            or self.cpu_cores <= 0
        ):
            raise ValueError("declaration cpu_cores must be a positive integer")

    def object(self) -> dict[str, Any]:
        """Return the field names consumed by the accepted schema-1.1 builder."""
        return {
            "cpu_type": self.cpu_type, "cpu_freq_mhz": self.cpu_freq_mhz,
            "cpu_cores": self.cpu_cores, "ram_gb": self.ram_gb,
            "gpu_type": self.gpu_model, "vram_gb": self.vram_gb,
        }


@dataclass(frozen=True, slots=True)
class TeamDeclarationIdentity:
    """Complete static identity supplied by one team for a final declaration."""

    group_id: str
    group_name: str
    members: tuple[str, ...]
    cop_repo: str
    thief_repo: str
    cop_mcp_url: str
    thief_mcp_url: str
    llm_model: str
    hardware: HardwareIdentity

    def __post_init__(self) -> None:
        """Fail before gameplay when mandatory declaration identity is incomplete."""
        validate_group_id(self.group_id)
        _nonempty(self.group_name, "group_name")
        if not isinstance(self.members, tuple) or not self.members or any(
            not isinstance(member, str) or not member.strip() for member in self.members
        ):
            raise ValueError("declaration members must contain non-empty names")
        _github_url(self.cop_repo, "cop_repo")
        _github_url(self.thief_repo, "thief_repo")
        _mcp_url(self.cop_mcp_url, "cop_mcp_url")
        _mcp_url(self.thief_mcp_url, "thief_mcp_url")
        _nonempty(self.llm_model, "llm_model")
        if not isinstance(self.hardware, HardwareIdentity):
            raise ValueError("declaration hardware must be HardwareIdentity")

    def object(self) -> dict[str, Any]:
        """Return the existing professor-builder identity shape without transport metadata."""
        return {
            "group_id": self.group_id, "group_name": self.group_name,
            "members": list(self.members),
            "repos": {"cop": self.cop_repo, "thief": self.thief_repo},
            "mcp_servers": {"cop": self.cop_mcp_url, "thief": self.thief_mcp_url},
            "llm_model": self.llm_model, "spec": self.hardware.object(),
        }


def validate_series_commits(
    commits: Mapping[int, Mapping[str, str]], group_ids: Sequence[str]
) -> dict[int, dict[str, str]]:
    """Require exact opaque commits for both groups in each of six sub-games."""
    groups = tuple(group_ids)
    if len(groups) != 2 or len(set(groups)) != 2:
        raise ValueError("series provenance requires exactly two groups")
    for group_id in groups:
        validate_group_id(group_id)
    if set(commits) != set(range(1, 7)):
        raise ValueError("series provenance requires sub-games 1 through 6")
    output: dict[int, dict[str, str]] = {}
    for number in range(1, 7):
        row = commits[number]
        if not isinstance(row, Mapping) or set(row) != set(groups):
            raise ValueError(f"sub-game {number} commit groups mismatch")
        output[number] = {}
        for group_id in groups:
            value = row[group_id]
            if not isinstance(value, str) or not value.strip() or value == UNRESOLVED_GIT_COMMIT:
                raise ValueError(f"sub-game {number} {group_id} commit is unresolved")
            output[number][group_id] = value
    return output
