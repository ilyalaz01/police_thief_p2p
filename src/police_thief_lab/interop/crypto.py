"""Exact reference-v3 commit/reveal dialect."""

from __future__ import annotations

import hashlib
import json
import secrets
from typing import Any


def canonical_json(payload: dict[str, Any]) -> str:
    return json.dumps(payload, sort_keys=True, ensure_ascii=False, separators=(",", ":"))


def hcommit(payload: dict[str, Any], nonce: str) -> str:
    return hashlib.sha256(f"{canonical_json(payload)}|{nonce}".encode()).hexdigest()


def seal(payload: dict[str, Any], nonce: str | None = None) -> dict[str, Any]:
    nonce = nonce or secrets.token_hex(16)
    return {"payload": payload, "nonce": nonce, "commit": hcommit(payload, nonce)}


def verify_records(records: list[dict[str, Any]]) -> tuple[bool, list[int]]:
    failed = [
        index
        for index, record in enumerate(records)
        if hcommit(record["payload"], record["nonce"]) != record["commit"]
    ]
    return not failed, failed
