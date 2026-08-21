"""Load one operator-supplied declaration file into the validated identity type."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .identity import HardwareIdentity, TeamDeclarationIdentity

REQUIRED_FIELDS = (
    "group_id", "group_name", "members", "cop_repo", "thief_repo",
    "cop_mcp_url", "thief_mcp_url", "llm_model", "hardware",
)
HARDWARE_FIELDS = ("cpu_type", "cpu_freq_mhz", "cpu_cores", "ram_gb", "gpu_model", "vram_gb")


def _require(raw: dict[str, Any], fields: tuple[str, ...], label: str) -> None:
    """Report every missing declaration field at once instead of one per run."""
    missing = [field for field in fields if raw.get(field) is None]
    if missing:
        raise ValueError(f"{label} is missing required values: {sorted(missing)}")


def load_declaration_identity(path: Path) -> TeamDeclarationIdentity:
    """Read one local declaration JSON file without inventing any absent value."""
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError("declaration file must contain one JSON object")
    _require(raw, REQUIRED_FIELDS, "declaration file")
    hardware = raw["hardware"]
    if not isinstance(hardware, dict):
        raise ValueError("declaration hardware must be a JSON object")
    _require(hardware, HARDWARE_FIELDS, "declaration hardware")
    members = raw["members"]
    if not isinstance(members, list):
        raise ValueError("declaration members must be a JSON array of names")
    return TeamDeclarationIdentity(
        group_id=raw["group_id"],
        group_name=raw["group_name"],
        members=tuple(members),
        cop_repo=raw["cop_repo"],
        thief_repo=raw["thief_repo"],
        cop_mcp_url=raw["cop_mcp_url"],
        thief_mcp_url=raw["thief_mcp_url"],
        llm_model=raw["llm_model"],
        hardware=HardwareIdentity(
            cpu_type=hardware["cpu_type"],
            cpu_freq_mhz=hardware["cpu_freq_mhz"],
            cpu_cores=hardware["cpu_cores"],
            ram_gb=hardware["ram_gb"],
            gpu_model=hardware["gpu_model"],
            vram_gb=hardware["vram_gb"],
        ),
    )
