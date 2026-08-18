"""Fail-closed Appendix-B schema-1.2 candidate and byte-lock operations."""

from __future__ import annotations

import copy
import hashlib
import json
import math
from dataclasses import dataclass
from typing import Any

from ..interop.crypto import canonical_json
from .config_schema import FIXED_VALUES, MINIMUM_VALUES, SECTION_FIELDS, TOP_LEVEL_FIELDS
from .identity import validate_group_id

APPENDIX_B_SCOPE = "official_appendix_b_schema_1_2"
APPENDIX_B_CANONICAL_COMPACT_V1 = "appendix_b_canonical_compact_v1"
PENDING_BILATERAL_APPROVAL = "LOCAL_PROPOSAL_PENDING_EXPLICIT_BILATERAL_AGREEMENT"
LOCKED_BILATERAL_APPROVAL = "EXPLICIT_BILATERAL_AGREEMENT_RECORDED"

@dataclass(frozen=True, slots=True)
class AppendixBConfigCandidate:
    """Local proposal in one named scope; it is not bilateral approval."""

    bytes: bytes
    sha256: str
    scope: str
    serialization_profile: str
    approval_status: str

    @property
    def value(self) -> dict[str, Any]:
        """Return a defensive copy reconstructed from the immutable locked bytes."""
        return json.loads(self.bytes.decode("utf-8"))


@dataclass(frozen=True, slots=True)
class AppendixBConfigLock:
    """Byte-identical candidate after explicit matching peer approval was recorded."""

    bytes: bytes
    sha256: str
    scope: str
    serialization_profile: str
    approval_status: str


def _validate_shape(value: dict[str, Any]) -> None:
    """Reject omitted, extra, or wrongly shaped official configuration fields."""
    if set(value) != TOP_LEVEL_FIELDS:
        raise ValueError("Appendix-B top-level fields mismatch")
    for section, fields in SECTION_FIELDS.items():
        if not isinstance(value.get(section), dict) or set(value[section]) != fields:
            raise ValueError(f"Appendix-B {section} fields mismatch")


def _validate_values(value: dict[str, Any]) -> None:
    """Enforce official fixed values, minima, identity, and positive negotiations."""
    if value["schema_version"] != "1.2":
        raise ValueError("schema_version must be 1.2")
    groups = value["agreed_between"]
    if not isinstance(groups, list) or len(groups) != 2:
        raise ValueError("agreed_between must contain two distinct group IDs")
    for group_id in groups:
        validate_group_id(group_id)
    if len(set(groups)) != 2:
        raise ValueError("agreed_between must contain two distinct group IDs")
    for (section, field), expected in FIXED_VALUES.items():
        if canonical_json({"value": value[section][field]}) != canonical_json({"value": expected}):
            raise ValueError(f"Appendix-B {field} must remain {expected!r}")
    gate = value["rate_limiter_gatekeeper"]
    for field, minimum in MINIMUM_VALUES.items():
        actual = gate[field]
        if (
            isinstance(actual, bool) or not isinstance(actual, int | float)
            or not math.isfinite(actual) or actual < minimum
        ):
            raise ValueError(f"Appendix-B {field} must be at least {minimum}")
    network = value["network_and_league"]
    for field in ("response_timeout_sec", "watchdog_timeout_sec", "token_budget_per_series"):
        actual = network[field]
        if (
            isinstance(actual, bool) or not isinstance(actual, int | float)
            or not math.isfinite(actual) or actual <= 0
        ):
            raise ValueError(f"Appendix-B {field} must be explicitly positive")


def build_appendix_b_candidate(
    value: dict[str, Any], *, serialization_profile: str
) -> AppendixBConfigCandidate:
    """Validate and serialize a local proposal without claiming peer agreement."""
    if serialization_profile != APPENDIX_B_CANONICAL_COMPACT_V1:
        raise ValueError("unsupported Appendix-B serialization profile")
    if not isinstance(value, dict):
        raise ValueError("Appendix-B configuration must be an object")
    cloned = copy.deepcopy(value)
    _validate_shape(cloned)
    _validate_values(cloned)
    payload = canonical_json(cloned).encode("utf-8")
    return AppendixBConfigCandidate(
        payload, hashlib.sha256(payload).hexdigest(), APPENDIX_B_SCOPE,
        serialization_profile, PENDING_BILATERAL_APPROVAL,
    )


def confirm_appendix_b_lock(
    candidate: AppendixBConfigCandidate, *, peer_sha256: str,
    peer_serialization_profile: str, bilateral_approval_recorded: bool,
) -> AppendixBConfigLock:
    """Refuse until the peer profile/hash match and explicit approval is recorded."""
    if (
        candidate.scope != APPENDIX_B_SCOPE
        or candidate.serialization_profile != APPENDIX_B_CANONICAL_COMPACT_V1
        or candidate.approval_status != PENDING_BILATERAL_APPROVAL
        or hashlib.sha256(candidate.bytes).hexdigest() != candidate.sha256
    ):
        raise ValueError("invalid local Appendix-B candidate")
    if peer_serialization_profile != candidate.serialization_profile:
        raise ValueError("Appendix-B serialization profile mismatch")
    if peer_sha256 != candidate.sha256:
        raise ValueError("Appendix-B byte lock mismatch")
    if bilateral_approval_recorded is not True:
        raise ValueError("explicit bilateral Appendix-B approval is required")
    return AppendixBConfigLock(
        candidate.bytes, candidate.sha256, candidate.scope,
        candidate.serialization_profile, LOCKED_BILATERAL_APPROVAL,
    )
