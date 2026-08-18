"""Contract tests for the distinct Appendix-B shared-config domain."""

from __future__ import annotations

import hashlib
from dataclasses import replace

import pytest

from police_thief_lab.interop.crypto import canonical_json
from police_thief_lab.league.config import (
    APPENDIX_B_CANONICAL_COMPACT_V1,
    APPENDIX_B_SCOPE,
    PENDING_BILATERAL_APPROVAL,
    build_appendix_b_candidate,
    confirm_appendix_b_lock,
)
from tests.support.league_fixtures import appendix_b_config


def test_appendix_b_candidate_has_its_own_named_bytes_and_pending_status() -> None:
    value = appendix_b_config()
    candidate = build_appendix_b_candidate(
        value,
        serialization_profile=APPENDIX_B_CANONICAL_COMPACT_V1,
    )
    expected = canonical_json(value).encode("utf-8")
    assert candidate.value == value
    assert candidate.bytes == expected
    assert candidate.sha256 == hashlib.sha256(expected).hexdigest()
    assert candidate.scope == APPENDIX_B_SCOPE
    assert candidate.approval_status == PENDING_BILATERAL_APPROVAL
    exposed = candidate.value
    exposed["network_and_league"]["num_games"] = 1
    assert candidate.value["network_and_league"]["num_games"] == 6


@pytest.mark.parametrize(
    ("section", "field", "value"),
    [
        ("network_and_league", "num_games", 1),
        ("scoring", "capture_cop", 19),
        ("pheromones", "pheromone_grid_size", 4),
        ("rate_limiter_gatekeeper", "requests_per_minute", 29),
        ("rate_limiter_gatekeeper", "concurrent_requests", 1),
        ("rate_limiter_gatekeeper", "retry_backoff_sec", 4),
        ("rate_limiter_gatekeeper", "max_retries", 2),
        ("rate_limiter_gatekeeper", "queue_depth", 99),
        ("network_and_league", "response_timeout_sec", float("nan")),
    ],
)
def test_appendix_b_fixed_values_and_minima_fail_closed(
    section: str, field: str, value: object
) -> None:
    config = appendix_b_config()
    config[section][field] = value
    with pytest.raises(ValueError, match=field):
        build_appendix_b_candidate(
            config,
            serialization_profile=APPENDIX_B_CANONICAL_COMPACT_V1,
        )


def test_appendix_b_shape_and_serialization_profile_are_exact() -> None:
    config = appendix_b_config()
    config["silent_extension"] = True
    with pytest.raises(ValueError, match="fields"):
        build_appendix_b_candidate(
            config,
            serialization_profile=APPENDIX_B_CANONICAL_COMPACT_V1,
        )
    with pytest.raises(ValueError, match="serialization profile"):
        build_appendix_b_candidate(
            appendix_b_config(), serialization_profile="pretty-json-assumption"
        )


def test_config_lock_requires_matching_peer_bytes_and_explicit_approval() -> None:
    candidate = build_appendix_b_candidate(
        appendix_b_config(),
        serialization_profile=APPENDIX_B_CANONICAL_COMPACT_V1,
    )
    with pytest.raises(ValueError, match="explicit bilateral"):
        confirm_appendix_b_lock(
            candidate,
            peer_sha256=candidate.sha256,
            peer_serialization_profile=candidate.serialization_profile,
            bilateral_approval_recorded=False,
        )
    with pytest.raises(ValueError, match="byte lock"):
        confirm_appendix_b_lock(
            candidate,
            peer_sha256="0" * 64,
            peer_serialization_profile=candidate.serialization_profile,
            bilateral_approval_recorded=True,
        )
    with pytest.raises(ValueError, match="serialization profile mismatch"):
        confirm_appendix_b_lock(
            candidate,
            peer_sha256=candidate.sha256,
            peer_serialization_profile="peer-pretty-json",
            bilateral_approval_recorded=True,
        )
    with pytest.raises(ValueError, match="invalid local"):
        confirm_appendix_b_lock(
            replace(candidate, bytes=b"{}"),
            peer_sha256=candidate.sha256,
            peer_serialization_profile=candidate.serialization_profile,
            bilateral_approval_recorded=True,
        )
    lock = confirm_appendix_b_lock(
        candidate,
        peer_sha256=candidate.sha256,
        peer_serialization_profile=candidate.serialization_profile,
        bilateral_approval_recorded=True,
    )
    assert lock.sha256 == candidate.sha256
    assert lock.bytes == candidate.bytes
