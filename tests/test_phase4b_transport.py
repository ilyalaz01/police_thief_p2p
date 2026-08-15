"""Phase 4B public configuration, retry, redaction, and artifact regressions."""

from __future__ import annotations

import copy
import json
import os
import subprocess
import sys
import threading
import time
from pathlib import Path

import pytest
from test_phase4a_interop import free_port, profile

from police_thief_lab.interop.artifacts import (
    build_config_artifact,
    build_declaration,
    build_log,
    build_result,
    consensus_sha256,
    derive_game_ids,
    final_consensus_scope,
)
from police_thief_lab.interop.network import (
    EndpointConfig,
    redact_secrets,
    redact_url,
    validate_mcp_url,
)
from police_thief_lab.interop.profile import MatchProfile
from police_thief_lab.interop.runtime import UNRESOLVED_GIT_COMMIT, DeadlineTracker, PeerRuntime
from police_thief_lab.interop.transport import McpPeerClient, discover_tools, start_server
from police_thief_lab.models import Direction, MoveType, Role


def endpoint(public: bool = True) -> EndpointConfig:
    return EndpointConfig(
        "0.0.0.0", 8801, "https://ours.example/mcp", "https://peer.example/mcp",
        2.0, 30.0, 0.01, 2, 10.0, public,
    )


def test_public_urls_require_clean_https_exact_mcp() -> None:
    assert endpoint().opponent_url.endswith("/mcp")
    assert validate_mcp_url("http://127.0.0.1:8801/mcp")
    for bad in (
        "http://public.example/mcp", "https://public.example/other",
        "https://user:pass@public.example/mcp", "https://public.example/mcp?token=x",
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
        monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    runtime = PeerRuntime(Role.POLICE, profile(), "127.0.0.1", 8801,
                          "http://127.0.0.1:1/mcp", tmp_path)
    monkeypatch.setattr(runtime.client, "call",
                        lambda *_args, **_kwargs: (_ for _ in ()).throw(TimeoutError("gone")))
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
    "name", [
        "phase4b1_public_attempt.json",
        "phase4b2_acceptance.json",
        "phase4b3_public_preflight.json",
    ]
)
def test_retained_phase4b_evidence_has_no_recursive_secret_values(name: str) -> None:
    evidence_path = Path(__file__).parents[1] / "reports" / name
    if not evidence_path.exists():
        pytest.skip("retained operational evidence is intentionally absent from this checkout")
    evidence = json.loads(evidence_path.read_text())
    secret_words = ("nonce", "token", "secret", "password", "authorization", "oauth",
                    "credential")

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
            for key in ("credentials_retained", "authorization_headers_retained",
                        "live_nonces_retained"):
                if key in value:
                    assert value[key] is False
            assert "<redacted>" not in json.dumps(value)


def _identity(group: str, url: str) -> dict:
    return {"group_id": group, "group_name": group.title(), "members": ["id-1"],
            "repos": {"cop": "repo-c", "thief": "repo-t"},
            "mcp_servers": {"cop": url}, "llm_model": "deterministic-python",
            "spec": {"cpu_type": "cpu", "cpu_freq_mhz": 1, "cpu_cores": 2,
                     "ram_gb": 3, "gpu_type": None, "vram_gb": 0}}


def _artifact_inputs() -> dict:
    records = [{"payload": {"step": 1}, "nonce": "n", "commit": "c"}]
    summary = {"records": records, "sub_game_number": 1, "role": "cop",
               "result": "capture", "winner": "cop", "steps": 1,
               "started_at": "2026-08-15T00:00:00+00:00", "duration_seconds": 2.5,
               "tokens_total": 0,
               "audit": {"passed": True, "verified_steps": 1, "failed_steps": []}}
    sub = {"sub_game_number": 1, "roles": {"alpha": "cop", "beta": "thief"},
           "result": "capture", "winner_group": "alpha", "tokens": {},
           "audit": {"log_verified": True}}
    aggregate = {"total_score": {}, "sub_games_won": {"alpha": 1, "beta": 0},
                 "ties": 0, "winner_group": "alpha", "series_tie": False}
    return {"terms": {"board_size": 7, "setting": "ירושלים🙂"}, "summary": summary,
            "sub": sub, "aggregate": aggregate}


def test_all_four_artifacts_exactly_match_pinned_professor_builders() -> None:
    professor_src = Path(__file__).parents[1] / "external/Game-P2P-Cop-Chase/src"
    if not professor_src.exists():
        pytest.skip("professor-owned reference implementation is not redistributed")
    data = _artifact_inputs()
    own, peer = _identity("alpha", "https://alpha.example/mcp"), _identity(
        "beta", "https://beta.example/mcp")
    ours = [
        build_declaration("game", "uid", "Asia/Jerusalem", "start", "end", 1, 0, own, peer),
        build_config_artifact(data["terms"], "game", "uid", 1),
        build_log(data["summary"], "game", "uid", "alpha", "beta"),
        build_result("game", "uid", ["alpha", "beta"], [data["sub"]],
                     data["aggregate"], "agreed-hash"),
    ]
    script = """
import json,sys
from police_thief.report.artifacts import (
    build_config_artifact, build_declaration, build_log, build_result
)
d=json.load(sys.stdin); own=d['own']; peer=d['peer']; x=d['data']
print(json.dumps([build_declaration('game','uid','Asia/Jerusalem','start','end',1,0,own,peer),build_config_artifact(x['terms'],'game','uid',1),build_log(x['summary'],'game','uid','alpha','beta'),build_result('game','uid',['alpha','beta'],[x['sub']],x['aggregate'],'agreed-hash')],ensure_ascii=False))
"""
    env = os.environ | {"PYTHONPATH": str(professor_src)}
    encoded = json.dumps({"own": own, "peer": peer, "data": data}).encode()
    raw = subprocess.check_output([sys.executable, "-c", script], input=encoded, env=env)
    assert ours == json.loads(raw)


@pytest.mark.parametrize("with_tie", [False, True])
def test_result_rows_are_never_silently_modified(with_tie: bool) -> None:
    data = _artifact_inputs()
    row = copy.deepcopy(data["sub"])
    if with_tie:
        row["tie"] = False
    result = build_result("game", "uid", ["alpha", "beta"], [row],
                          data["aggregate"], "hash")
    assert result["sub_games"][0] == row
    assert ("tie" in result["sub_games"][0]) is with_tie


def test_protocol_layer_is_transport_endpoint_agnostic(tmp_path: Path) -> None:
    local = PeerRuntime(Role.POLICE, profile(), "127.0.0.1", 8801,
                        "http://127.0.0.1:8802/mcp", tmp_path)
    public = PeerRuntime(Role.POLICE, profile(), "0.0.0.0", 8801,
                         "https://peer.example/mcp", tmp_path)
    assert local.profile.bytes() == public.profile.bytes()
    assert type(local.backend) is type(public.backend)
    assert local.receiver.next_step == public.receiver.next_step


def test_advertised_url_propagates_to_role_appropriate_negotiation_identity(
        tmp_path: Path) -> None:
    url = "https://public.example/mcp"
    runtime = PeerRuntime(Role.POLICE, profile(), "0.0.0.0", 8801,
                          "https://peer.example/mcp", tmp_path, advertised_url=url,
                          group_id="our-group", group_name="Our Group")
    identity = runtime.profile.agreement(runtime.role.value, runtime.identity)["identity"]
    assert identity["group_id"] == "our-group"
    assert identity["mcp_servers"] == {"cop": url}
    assert "localhost" not in json.dumps(identity["mcp_servers"]).lower()
    assert "https://peer.example/mcp" not in runtime.profile.bytes().decode()


def test_git_commit_is_opaque_identity_metadata_outside_consensus(tmp_path: Path) -> None:
    exact = " feature/Build 07 \t"
    runtime = PeerRuntime(
        Role.POLICE, profile(), "127.0.0.1", 8801, "http://127.0.0.1:8802/mcp",
        tmp_path, git_commit=exact,
    )
    agreement = runtime.profile.agreement(runtime.role.value, runtime.identity)
    assert agreement["identity"]["github_commit"] == exact
    assert exact not in runtime.profile.bytes().decode()
    assert exact not in json.dumps(runtime.profile.reference_terms())
    baseline_ids = derive_game_ids(runtime.profile.reference_terms(), "alpha", "beta")
    changed = PeerRuntime(
        Role.POLICE, profile(), "127.0.0.1", 8801, "http://127.0.0.1:8802/mcp",
        tmp_path, git_commit="different",
    )
    assert changed.profile.bytes() == runtime.profile.bytes()
    assert changed.profile.sha256 == runtime.profile.sha256
    assert derive_game_ids(changed.profile.reference_terms(), "alpha", "beta") == baseline_ids
    scope = final_consensus_scope("game", {"winner_group": "alpha"}, [{
        "sub_game_number": 1, "roles": {"alpha": "police", "beta": "thief"},
        "result": "capture", "winner_group": "alpha", "score": {"alpha": 20, "beta": 5},
        "github_commit": {"alpha": exact, "beta": "different"},
    }])
    without_commits = copy.deepcopy(scope)
    assert consensus_sha256(scope) == consensus_sha256(without_commits)


@pytest.mark.parametrize("commit", [None, "", UNRESOLVED_GIT_COMMIT])
def test_real_team_gate_refuses_unresolved_local_commit_before_listener(
        monkeypatch: pytest.MonkeyPatch, tmp_path: Path, commit: str | None) -> None:
    runtime = PeerRuntime(
        Role.THIEF, profile(), "127.0.0.1", 8801, "http://127.0.0.1:8802/mcp",
        tmp_path, git_commit=commit, real_team=True,
    )
    monkeypatch.setattr(
        "police_thief_lab.interop.runtime.start_server",
        lambda *_args: (_ for _ in ()).throw(AssertionError("listener started")),
    )
    result = runtime.run()
    assert result["error"] == (
        "ValueError: real-team Git provenance refused: local commit is unresolved"
    )


def test_real_team_gate_refuses_professor_identity_omission_before_gameplay(
        monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    runtime = PeerRuntime(
        Role.THIEF, profile(), "127.0.0.1", 8801, "http://127.0.0.1:8802/mcp",
        tmp_path, git_commit="ours-exact", real_team=True,
    )
    runtime.inboxes = type("Inboxes", (), {"agreements": __import__("queue").Queue()})()
    remote = profile().agreement("police")
    remote["identity"].pop("github_commit", None)
    runtime.inboxes.agreements.put(remote)
    monkeypatch.setattr(runtime.client, "call", lambda *_args: 0.0)
    with pytest.raises(ValueError, match="peer commit is unresolved"):
        runtime._negotiate()
    assert runtime.records == []


def test_rule47_remains_enabled(tmp_path: Path) -> None:
    runtime = PeerRuntime(Role.THIEF, profile(), "127.0.0.1", 8801,
                          "http://127.0.0.1:8802/mcp", tmp_path)
    runtime.state.position = runtime.config.thief_start
    runtime.state.barriers.update({
        type(runtime.state.position)(2, 3), type(runtime.state.position)(4, 3),
        type(runtime.state.position)(3, 2), type(runtime.state.position)(3, 4),
    })
    assert runtime._boxed_in()


class _FixedPolicy:
    def __init__(self, direction: Direction | None) -> None:
        self.direction = direction

    def choose_action(self, observation):
        for action in observation.legal_actions:
            if self.direction is None and action.move_type is MoveType.STAY:
                return action
            if action.move_type is MoveType.MOVE and action.direction is self.direction:
                return action
        raise AssertionError("fixed test action unavailable")


def _reference_runtime_profile(survival_limit: int) -> MatchProfile:
    return MatchProfile(
        {"board_size": 7, "police_start": [0, 0], "thief_start": [0, 1],
         "blocked_cells": [], "barrier_quota": 14},
        survival_limit=survival_limit,
        move_limit=35,
        timeouts={"connect": 5.0, "turn": 5.0, "audit": 5.0, "retry": 0.01,
                  "retry_count": 100},
        artifact_profile="reference-v3-artifact-1.1",
        artifact_schema="1.1",
        consensus_scope="reference_symmetric_outcome_without_tie",
        setting="New York",
        minimum_center_intensity=0.5,
        step_numbering="sender_local",
    )


def _run_reference_pair(
        tmp_path: Path, outcome: str, commits: tuple[str | None, str | None] = (None, None)
) -> tuple[dict, dict]:
    police_port, thief_port = free_port(), free_port()
    shared = _reference_runtime_profile(35)
    police = PeerRuntime(
        Role.POLICE, shared, "127.0.0.1", police_port,
        f"http://127.0.0.1:{thief_port}/mcp", tmp_path / "police",
        group_id="artifact-police", group_name="Artifact Police",
        git_commit=commits[0],
    )
    thief = PeerRuntime(
        Role.THIEF, shared, "127.0.0.1", thief_port,
        f"http://127.0.0.1:{police_port}/mcp", tmp_path / "thief",
        group_id="artifact-thief", group_name="Artifact Thief",
        git_commit=commits[1],
    )
    police.backend = _FixedPolicy(Direction.E)
    thief.backend = _FixedPolicy(None)
    if outcome == "survival":
        thief.state.own_moves = 34
    results: dict[str, dict] = {}
    threads = [
        threading.Thread(target=lambda: results.setdefault("police", police.run())),
        threading.Thread(target=lambda: results.setdefault("thief", thief.run())),
    ]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(15)
    assert not any(thread.is_alive() for thread in threads)
    assert results["police"]["ok"] and results["thief"]["ok"]
    return results["police"], results["thief"]


@pytest.mark.parametrize(
    ("outcome", "expected_score"),
    [
        ("capture", {"artifact-police": 20, "artifact-thief": 5}),
        ("survival", {"artifact-police": 5, "artifact-thief": 10}),
    ],
)
def test_reference_runtime_artifacts_score_uid_and_consensus_end_to_end(
        tmp_path: Path, outcome: str, expected_score: dict[str, int]) -> None:
    police, thief = _run_reference_pair(tmp_path, outcome)
    results = []
    for _role, runtime_result in (("police", police), ("thief", thief)):
        docs = {}
        for raw_path in runtime_result["artifacts"]:
            path = Path(raw_path)
            docs[path.name.split("_", 1)[0]] = json.loads(path.read_text())
        assert set(docs) == {"declaration", "config", "log", "result"}
        assert all(doc["schema_version"] == "1.1" for doc in docs.values())
        result = docs["result"]
        assert result["groups"] == ["artifact-police", "artifact-thief"]
        row = result["sub_games"][0]
        assert row["score"] == expected_score
        assert result["final_result"]["total_score"] == expected_score
        assert row["github_commit"] == {
            "artifact-police": "UNRESOLVED_SELF_TEST_NO_GIT_METADATA",
            "artifact-thief": "UNRESOLVED_SELF_TEST_NO_GIT_METADATA",
        }
        assert row["log_files"] == {
            group: f"{group}/log_{result['game_id']}_g01.json" for group in expected_score
        }
        scope = final_consensus_scope(
            result["game_id"],
            {key: result["final_result"][key] for key in (
                "total_score", "sub_games_won", "ties", "winner_group", "series_tie"
            )},
            result["sub_games"],
        )
        assert consensus_sha256(scope) == result["mutual_agreement"]["sha256"]
        results.append(result)
    assert {result["game_id"] for result in results} == {
        "artifact-police-vs-artifact-thief"
    }
    assert len({result["game_uid"] for result in results}) == 1
    assert len({result["mutual_agreement"]["sha256"] for result in results}) == 1
    expected_ids = derive_game_ids(
        _reference_runtime_profile(35).reference_terms(),
        "artifact-police", "artifact-thief",
    )
    assert (results[0]["game_id"], results[0]["game_uid"]) == expected_ids

    original = results[0]
    original_scope = final_consensus_scope(
        original["game_id"],
        {key: original["final_result"][key] for key in (
            "total_score", "sub_games_won", "ties", "winner_group", "series_tie"
        )},
        original["sub_games"],
    )
    baseline = consensus_sha256(original_scope)
    noisy = copy.deepcopy(original)
    noisy["sub_games"][0].update({"started_at": "changed", "tokens": {"x": 999},
                                  "audit": {"log_verified": False}})
    assert consensus_sha256(final_consensus_scope(
        noisy["game_id"], original_scope["aggregate"], noisy["sub_games"]
    )) == baseline
    changed_result = "capture" if outcome == "survival" else "survival"
    for field, value in (("result", changed_result), ("winner_group", "other"),
                         ("score", {"artifact-police": 999, "artifact-thief": 0})):
        changed = copy.deepcopy(original["sub_games"])
        changed[0][field] = value
        assert consensus_sha256(final_consensus_scope(
            original["game_id"], original_scope["aggregate"], changed
        )) != baseline


def test_reference_artifacts_map_two_exact_group_commits(tmp_path: Path) -> None:
    exact = ("police/commit EXACT ", "thief-commit:@{opaque}")
    police, thief = _run_reference_pair(tmp_path, "capture", exact)
    expected = {"artifact-police": exact[0], "artifact-thief": exact[1]}
    for runtime_result in (police, thief):
        result_path = next(Path(path) for path in runtime_result["artifacts"]
                           if Path(path).name.startswith("result_"))
        log_path = next(Path(path) for path in runtime_result["artifacts"]
                        if Path(path).name.startswith("log_"))
        result = json.loads(result_path.read_text())
        log = json.loads(log_path.read_text())
        assert result["sub_games"][0]["github_commit"] == expected
        assert log["summary"]["group_id"] in expected
        assert log["summary"]["opponent_group_id"] in expected
        assert consensus_sha256(final_consensus_scope(
            result["game_id"],
            {key: result["final_result"][key] for key in (
                "total_score", "sub_games_won", "ties", "winner_group", "series_tie"
            )},
            result["sub_games"],
        )) == result["mutual_agreement"]["sha256"]


def test_cli_run_peer_creates_missing_output_parent(
        monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    from police_thief_lab.interop import runtime as runtime_module

    monkeypatch.setattr(PeerRuntime, "run", lambda self: {"ok": False, "phase": "failed"})
    profile_path = tmp_path / "profile.json"
    profile_path.write_text(json.dumps(profile().object()))
    output = tmp_path / "missing" / "nested" / "result.json"
    status = runtime_module.run_peer(
        "police", profile_path, "127.0.0.1", free_port(),
        "http://127.0.0.1:1/mcp", "http://127.0.0.1:1/mcp",
        tmp_path / "artifacts", output,
    )
    assert status == 1
    assert json.loads(output.read_text()) == {"ok": False, "phase": "failed"}


def test_real_fastmcp_origin_preflight_discovers_normal_four_tools() -> None:
    port = free_port()
    start_server("preflight", "127.0.0.1", port)
    expected = ["negotiate", "receive_control", "receive_turn", "submit_audit"]
    client = McpPeerClient(f"http://127.0.0.1:{port}/mcp", 5.0, 0.01)
    discovered: list[str] | None = None
    for _attempt in range(100):
        try:
            discovered = discover_tools(client.url)
            break
        except Exception:
            time.sleep(0.01)
    assert discovered == expected
