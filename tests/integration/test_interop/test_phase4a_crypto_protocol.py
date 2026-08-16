"""Phase 4A commitment, delivery, and profile checks."""

import json

import pytest

from police_thief_lab.interop.crypto import canonical_json, hcommit
from police_thief_lab.interop.protocol import Equivocation, ProtocolViolation, TurnInbox
from tests.support.interop_test_support import ROOT, frame, profile


def test_all_hcommit_golden_vectors_and_extra_fields() -> None:
    vectors = json.loads(
        (ROOT / "interop/golden_vectors/hcommit_reference_vs_kit.json").read_text(encoding="utf-8")
    )["vectors"]
    for vector in vectors:
        assert canonical_json(vector["payload"]) == vector["canonical"]
        assert hcommit(vector["payload"], vector["nonce"]) == vector["expected_sha256"]
    payload = {"step": 1, "hint": "עברית🙂", "float": 1e-7}
    assert hcommit(payload, "n") != hcommit(payload | {"extra": None}, "n")


def test_delivery_duplicate_equivocation_buffer_stale_and_window() -> None:
    inbox = TurnInbox(window=2)
    assert inbox.offer(frame(2, "b" * 64)) == []
    ready = inbox.offer(frame(1))
    assert [message.step for message in ready] == [1, 2]
    assert inbox.offer(frame(1)) == []
    assert inbox.absorbed == 1
    with pytest.raises(Equivocation):
        inbox.offer(frame(2, "c" * 64))
    with pytest.raises(ProtocolViolation):
        inbox.offer(frame(6))


def test_profile_requires_byte_identical_config() -> None:
    own = profile()
    own.verify_agreement(own.agreement("thief"))
    changed = own.agreement("thief")
    changed["identity"]["config_bytes_hex"] += "0a"
    with pytest.raises(ValueError, match="byte-identical"):
        own.verify_agreement(changed)
