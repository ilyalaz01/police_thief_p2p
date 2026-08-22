"""Offline contract for the official counted-series result mail."""

from __future__ import annotations

import base64
import email
import json
from pathlib import Path

import pytest

from police_thief_lab.reporting import (
    GmailResultSender,
    ReportingNotAuthorizedError,
    SendFailedError,
    TransportStatusError,
    build_result_message,
    load_reporting_config,
)

CONFIG = {
    "schema_version": "reporting-1.0",
    "league_recipient": "league@example.com",
    "sender_address": "team@example.com",
    "subject_template": "Police-Thief P2P counted result {game_id}",
    "attachment_name_template": "result_{game_id}.json",
    "max_sends_per_game": 1,
    "retry_attempts": 3,
    "initial_backoff_seconds": 1,
    "max_backoff_seconds": 4,
}
RESULT = {
    "schema_version": "1.1",
    "report_type": "final_game_result",
    "game_id": "il-nv-ai-vs-vm__fabi",
    "groups": ["il-nv-ai", "vm__fabi"],
    "final_result": {"winner_group": "vm__fabi"},
    "mutual_agreement": {"sha256": "a" * 64, "confirmed": True},
}


def _config(tmp_path: Path, **overrides: object):
    """Write and load one reporting configuration."""
    path = tmp_path / "reporting.json"
    path.write_text(json.dumps({**CONFIG, **overrides}, ensure_ascii=False), encoding="utf-8")
    return load_reporting_config(path)


def _result_bytes() -> bytes:
    """Return the exact result bytes an operator would mail."""
    return json.dumps(RESULT, ensure_ascii=False, indent=2).encode("utf-8")


def test_body_and_single_attachment_carry_the_identical_result_bytes(tmp_path: Path) -> None:
    message = build_result_message(_result_bytes(), _config(tmp_path))
    parsed = email.message_from_bytes(base64.urlsafe_b64decode(message.raw))
    attachments = [part for part in parsed.walk() if part.get_filename()]
    assert len(attachments) == 1
    assert attachments[0].get_filename() == "result_il-nv-ai-vs-vm__fabi.json"
    assert attachments[0].get_payload(decode=True) == _result_bytes()
    assert message.body == _result_bytes().decode("utf-8")
    assert parsed["To"] == "league@example.com"
    assert "il-nv-ai-vs-vm__fabi" in parsed["Subject"]


def test_a_result_without_mutual_agreement_is_refused(tmp_path: Path) -> None:
    without = {key: value for key, value in RESULT.items() if key != "mutual_agreement"}
    payload = json.dumps(without, ensure_ascii=False).encode("utf-8")
    with pytest.raises(ValueError, match="mutual_agreement"):
        build_result_message(payload, _config(tmp_path))


def test_sending_without_an_authorized_transport_is_refused(tmp_path: Path) -> None:
    config = _config(tmp_path)
    message = build_result_message(_result_bytes(), config)
    sender = GmailResultSender(config)
    assert sender.dry_run(message)["sent"] is False
    with pytest.raises(ReportingNotAuthorizedError):
        sender.send(message)


def test_one_accepted_send_per_game_is_enforced(tmp_path: Path) -> None:
    config = _config(tmp_path)
    message = build_result_message(_result_bytes(), config)
    sender = GmailResultSender(config, transport=lambda raw: {"id": "provider-1"})
    first = sender.send(message)
    assert first["sent"] is True and first["attempts"] == 1
    assert first["provider_message_id"] == "provider-1"
    with pytest.raises(SendFailedError, match="send limit"):
        sender.send(message)


def test_retryable_statuses_back_off_and_then_succeed(tmp_path: Path) -> None:
    config = _config(tmp_path)
    message = build_result_message(_result_bytes(), config)
    statuses, waits = [429, 503], []

    def transport(raw: str) -> dict[str, str]:
        if statuses:
            raise TransportStatusError(statuses.pop(0))
        return {"id": "provider-2"}

    sender = GmailResultSender(config, transport=transport, sleep=waits.append)
    outcome = sender.send(message)
    assert outcome["attempts"] == 3
    assert outcome["retried_statuses"] == [429, 503]
    assert waits == [1, 2]


def test_a_permanent_status_is_not_retried(tmp_path: Path) -> None:
    config = _config(tmp_path)
    message = build_result_message(_result_bytes(), config)
    calls, waits = [], []

    def transport(raw: str) -> dict[str, str]:
        calls.append(raw)
        raise TransportStatusError(403)

    sender = GmailResultSender(config, transport=transport, sleep=waits.append)
    with pytest.raises(SendFailedError, match=r"\[403\]"):
        sender.send(message)
    assert len(calls) == 1 and waits == []


def test_reporting_configuration_refuses_incomplete_or_unknown_input(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="missing values"):
        _config(tmp_path, league_recipient=None)
    with pytest.raises(ValueError, match="not the supported"):
        _config(tmp_path, schema_version="reporting-0.9")
    with pytest.raises(ValueError, match="plain e-mail address"):
        _config(tmp_path, sender_address="not-an-address")
    with pytest.raises(ValueError, match="must contain"):
        _config(tmp_path, subject_template="no placeholder")


def test_no_summary_field_can_carry_a_credential(tmp_path: Path) -> None:
    config = _config(tmp_path)
    message = build_result_message(_result_bytes(), config)
    sender = GmailResultSender(config, transport=lambda raw: {"id": "x", "token": "SECRET"})
    outcome = sender.send(message)
    assert "SECRET" not in json.dumps(outcome)


class _DraftTransport:
    """Minimal transport double exposing only the draft boundary."""

    def __init__(self) -> None:
        """Record what the sender would place in drafts."""
        self.drafted: list[str] = []

    def create_draft(self, raw: str) -> dict[str, object]:
        """Accept one draft and report a provider identifier."""
        self.drafted.append(raw)
        return {"id": "draft-1", "delivered": False, "awaiting_manual_send": True}

    def __call__(self, raw: str) -> dict[str, object]:
        """Refuse to send; this double exists to prove drafting never delivers."""
        raise AssertionError("the draft path must never send")


def test_drafting_never_delivers_and_never_counts_as_a_send(tmp_path: Path) -> None:
    config = _config(tmp_path)
    message = build_result_message(_result_bytes(), config)
    transport = _DraftTransport()
    sender = GmailResultSender(config, transport=transport)
    record = sender.draft(message)
    assert record["sent"] is False and record["delivered"] is False
    assert record["provider_message_id"] == "draft-1"
    assert transport.drafted == [message.raw]
    assert sender.accepted == {}


def test_drafting_without_a_draft_capable_transport_is_refused(tmp_path: Path) -> None:
    config = _config(tmp_path)
    message = build_result_message(_result_bytes(), config)
    with pytest.raises(ReportingNotAuthorizedError):
        GmailResultSender(config, transport=lambda raw: {"id": "x"}).draft(message)
