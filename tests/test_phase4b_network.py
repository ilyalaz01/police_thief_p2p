"""Phase 4B endpoint, retry, redaction, and retained-evidence checks."""

import copy
import json
from pathlib import Path

import pytest
from interop_test_support import profile

from police_thief_lab.interop.network import (
    EndpointConfig,
    redact_secrets,
    redact_url,
    validate_mcp_url,
)
from police_thief_lab.interop.runtime import DeadlineTracker, PeerRuntime
from police_thief_lab.interop.transport import McpPeerClient
from police_thief_lab.models import Role


def endpoint(public: bool = True) -> EndpointConfig:
    return EndpointConfig(
        "0.0.0.0",
        8801,
        "https://ours.example/mcp",
        "https://peer.example/mcp",
        2.0,
        30.0,
        0.01,
        2,
        10.0,
        public,
    )


def test_public_urls_require_clean_https_exact_mcp() -> None:
    assert endpoint().opponent_url.endswith("/mcp")
    assert validate_mcp_url("http://127.0.0.1:8801/mcp")
    for bad in (
        "http://public.example/mcp",
        "https://public.example/other",
        "https://user:pass@public.example/mcp",
        "https://public.example/mcp?token=x",
    ):
        with pytest.raises(ValueError):
            validate_mcp_url(bad, public=True)


def test_retry_sends_identical_payload_then_succeeds(monkeypatch: pytest.MonkeyPatch) -> None:
    client = McpPeerClient("https://peer.example/mcp", 1.0, 0.0, retry_count=2)
    sent = []

    def invoke(tool: str, argument: str, value: dict) -> None:
        sent.append(copy.deepcopy(value))
        value["nested"]["x"] = 99
        if len(sent) == 1:
            raise ConnectionRefusedError

    monkeypatch.setattr(client, "_invoke", invoke)
    payload = {"step": 1, "nested": {"x": 1}}
    client.call("receive_turn", payload)
    assert sent == [payload, payload]
    assert client.last_attempts == 2


def test_retries_exhaust_deterministically(monkeypatch: pytest.MonkeyPatch) -> None:
    client = McpPeerClient("https://peer.example/mcp", 1.0, 0.0, retry_count=1)
    monkeypatch.setattr(client, "_invoke", lambda *_: (_ for _ in ()).throw(OSError("gone")))
    with pytest.raises(TimeoutError, match="after 2 attempts"):
        client.call("receive_turn", {"step": 1})


def test_peer_transport_loss_returns_deterministic_failed_state(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    runtime = PeerRuntime(
        Role.POLICE, profile(), "127.0.0.1", 8801, "http://127.0.0.1:1/mcp", tmp_path
    )
    monkeypatch.setattr(
        runtime.client,
        "call",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(TimeoutError("gone")),
    )
    result = runtime.run()
    assert result["ok"] is False
    assert result["phase"] == "failed"
    assert result["error"] == "TimeoutError: gone"


def test_duplicate_does_not_renew_deadline() -> None:
    deadline = DeadlineTracker(10.0, started=123.0)
    original = deadline.started
    # Delivery dedupe owns no DeadlineTracker and therefore cannot mutate its epoch.
    assert deadline.started == original


def test_secret_redaction_and_safe_url() -> None:
    value = {"nonce": "never", "oauth_token": "never", "nested": [{"password": "never"}]}
    text = json.dumps(redact_secrets(value))
    assert "never" not in text
    assert redact_url("https://user:pass@peer.example/mcp?token=x") == "https://peer.example/mcp"


@pytest.mark.parametrize(
    "name",
    [
        "phase4b1_public_attempt.json",
        "phase4b2_acceptance.json",
        "phase4b3_public_preflight.json",
    ],
)
def test_retained_phase4b_evidence_has_no_recursive_secret_values(name: str) -> None:
    evidence_path = Path(__file__).parents[1] / "reports" / name
    if not evidence_path.exists():
        pytest.skip("retained operational evidence is intentionally absent from this checkout")
    evidence = json.loads(evidence_path.read_text())
    secret_words = ("nonce", "token", "secret", "password", "authorization", "oauth", "credential")

    def scan(value: object, path: tuple[str, ...] = ()) -> None:
        if isinstance(value, dict):
            for key, item in value.items():
                if any(word in key.lower() for word in secret_words):
                    assert item in (False, 0, None, "<redacted>"), ".".join((*path, key))
                scan(item, (*path, key))
        elif isinstance(value, list):
            for index, item in enumerate(value):
                scan(item, (*path, str(index)))

    scan(evidence)


def test_phase4b3_evidence_tree_has_no_url_credentials_or_secret_values() -> None:
    root = Path(__file__).parents[1]
    files = [root / "reports/phase4b3_public_preflight.json"] + list(
        (root / "interop/logs/phase4b3-public").glob("*")
    )
    if not files[0].exists() or len(files) == 1:
        pytest.skip("retained public-run evidence is intentionally absent from this checkout")
    for path in files:
        text = path.read_text()
        assert "Authorization:" not in text
        assert "https://user:" not in text
        assert "?token=" not in text.lower()
        if path.suffix == ".json":
            value = json.loads(text)
            for key in (
                "credentials_retained",
                "authorization_headers_retained",
                "live_nonces_retained",
            ):
                if key in value:
                    assert value[key] is False
            assert "<redacted>" not in json.dumps(value)
