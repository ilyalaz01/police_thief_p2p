"""Private reference-compatible artifact formatting helpers."""
# ruff: noqa: E501 -- formatting bodies are preserved verbatim.

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timedelta
from typing import Any

from .crypto import canonical_json

LINKS_REMARK = "These are logical roles, NOT fixed filenames. Each actual file name MUST be derived from the game_id so that files from different games are never mixed. Match-level files (declaration, result) are named <role>_<game_id>.json; per-sub-game files (config, log) are named <role>_<game_id>_g<NN>.json where <NN> is the sub_game_number. The names below are examples for game_id=S01R02-team07-vs-team13."


def pretty_bytes(value: dict[str, Any]) -> bytes:
    """Perform pretty bytes through the documented module contract."""
    return json.dumps(value, ensure_ascii=False, indent=2).encode("utf-8")


def canonical_sha256(value: Any) -> str:
    """Perform canonical sha256 through the documented module contract."""
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def consensus_sha256(value: Any) -> str:
    """Perform consensus sha256 through the documented module contract."""
    serialized = json.dumps(value, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


def artifact_links(game_id: str) -> dict[str, str]:
    """Perform artifact links through the documented module contract."""
    return {"_remark": LINKS_REMARK, "declaration": f"declaration_{game_id}.json",
            "config": f"config_{game_id}_g<NN>.json", "log": f"log_{game_id}_g<NN>.json",
            "result": f"result_{game_id}.json"}


def _hardware(spec: dict[str, Any]) -> dict[str, Any]:
    """Compute the internal hardware step used by module."""
    return {"cpu_type": spec.get("cpu_type"), "cpu_freq_mhz": spec.get("cpu_freq_mhz"),
            "cpu_cores": spec.get("cpu_cores"), "ram_gb": spec.get("ram_gb"),
            "gpu_model": spec.get("gpu_type"), "vram_gb": spec.get("vram_gb")}


def _group(identity: dict[str, Any]) -> dict[str, Any]:
    """Compute the internal group step used by module."""
    block = {"group_id": identity["group_id"], "group_name": identity["group_name"],
             "members": identity["members"], "repos": identity["repos"],
             "mcp_servers": identity["mcp_servers"], "llm_model": identity["llm_model"],
             "hardware_spec": _hardware(identity["spec"])}
    block["signature"] = consensus_sha256(block)
    return block


def _ended_at(started_at: str, duration_seconds: float) -> str:
    """Compute the internal ended at step used by module."""
    try:
        return (datetime.fromisoformat(started_at) + timedelta(seconds=duration_seconds)).isoformat()
    except (TypeError, ValueError):
        return started_at
