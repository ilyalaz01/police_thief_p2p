"""Offline contract for the send-only Gmail transport and its one-time authorization."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from police_thief_lab.reporting import (
    SEND_SCOPE,
    GmailApiTransport,
    GmailCredentials,
    TransportStatusError,
    authorization_url,
    exchange_code,
    load_gmail_credentials,
    save_gmail_credentials,
)

CREDENTIALS = GmailCredentials(
    client_id="client-id.apps.googleusercontent.com",
    client_secret="client-secret-value",
    refresh_token="refresh-token-value",
)


def _transport(token_status: int = 200, send_status: int = 200) -> tuple[GmailApiTransport, list]:
    """Build one transport whose two HTTPS calls are recorded instead of performed."""
    calls: list = []

    def form(url: str, fields: dict) -> tuple[int, dict]:
        calls.append(("form", url, fields))
        return token_status, {"access_token": "short-lived", "expires_in": 3599}

    def json_post(url: str, payload: dict, bearer: str) -> tuple[int, dict]:
        calls.append(("json", url, payload, bearer))
        return send_status, {"id": "provider-id", "threadId": "thread-id"}

    return GmailApiTransport(CREDENTIALS, form_poster=form, json_poster=json_post), calls


def test_the_refresh_token_is_exchanged_and_only_the_raw_message_is_posted() -> None:
    transport, calls = _transport()
    outcome = transport("cmF3LW1lc3NhZ2U=")
    assert outcome == {"id": "provider-id", "threadId": "thread-id"}
    kinds = [call[0] for call in calls]
    assert kinds == ["form", "json"]
    assert calls[0][2]["grant_type"] == "refresh_token"
    assert calls[1][1].endswith("/messages/send")
    assert calls[1][2] == {"raw": "cmF3LW1lc3NhZ2U="}
    assert calls[1][3] == "short-lived"


@pytest.mark.parametrize("status", [401, 429, 500])
def test_a_failed_token_exchange_surfaces_its_status(status: int) -> None:
    transport, _ = _transport(token_status=status)
    with pytest.raises(TransportStatusError) as error:
        transport("cmF3")
    assert error.value.status == status


def test_a_refused_send_surfaces_its_status_without_a_body() -> None:
    transport, _ = _transport(send_status=403)
    with pytest.raises(TransportStatusError) as error:
        transport("cmF3")
    assert error.value.status == 403
    assert "403" in str(error.value)


def test_the_consent_url_requests_only_the_send_scope() -> None:
    url = authorization_url("client-id", "http://127.0.0.1:8765/")
    assert url.startswith("https://accounts.google.com/o/oauth2/v2/auth?")
    assert "access_type=offline" in url and "prompt=consent" in url
    assert SEND_SCOPE.replace(":", "%3A").replace("/", "%2F") in url
    assert "gmail.send" in url


def test_the_exchange_requires_a_refresh_token_in_the_response() -> None:
    def without_refresh(url: str, fields: dict) -> tuple[int, dict]:
        return 200, {"access_token": "only-short-lived"}

    with pytest.raises(RuntimeError, match="no refresh token"):
        exchange_code("id", "secret", "code", "http://127.0.0.1:8765/", poster=without_refresh)


def test_a_refused_exchange_reports_its_status() -> None:
    with pytest.raises(RuntimeError, match="status 400"):
        exchange_code(
            "id", "secret", "code", "http://127.0.0.1:8765/",
            poster=lambda url, fields: (400, {"error": "invalid_grant"}),
        )


def test_credentials_round_trip_without_revealing_a_secret(tmp_path: Path) -> None:
    path = save_gmail_credentials(tmp_path / "gmail.json", CREDENTIALS)
    loaded = load_gmail_credentials(path)
    assert loaded == CREDENTIALS
    summary = loaded.redacted()
    assert summary["client_secret"] == "<redacted>"
    assert summary["refresh_token"] == "<redacted>"
    assert "refresh-token-value" not in json.dumps(summary)
    assert summary["scope"] == SEND_SCOPE


def test_placeholder_or_empty_credentials_are_refused(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="placeholder"):
        GmailCredentials("REPLACE_WITH_CLIENT_ID", "s", "r")
    with pytest.raises(ValueError, match="is empty"):
        GmailCredentials("id", "  ", "r")
    incomplete = tmp_path / "partial.json"
    incomplete.write_text(json.dumps({"client_id": "id"}), encoding="utf-8")
    with pytest.raises(ValueError, match="missing values"):
        load_gmail_credentials(incomplete)


def test_a_non_https_endpoint_is_refused() -> None:
    with pytest.raises(ValueError, match="HTTPS"):
        GmailCredentials("id", "secret", "refresh", token_uri="http://oauth.example/token")


def test_a_draft_is_created_without_sending() -> None:
    transport, calls = _transport()
    outcome = transport.create_draft("cmF3")
    assert outcome["delivered"] is False and outcome["awaiting_manual_send"] is True
    assert calls[1][1].endswith("/drafts")
    assert calls[1][2] == {"message": {"raw": "cmF3"}}


def test_a_refused_draft_surfaces_its_status() -> None:
    transport, _ = _transport(send_status=500)
    with pytest.raises(TransportStatusError) as error:
        transport.create_draft("cmF3")
    assert error.value.status == 500
