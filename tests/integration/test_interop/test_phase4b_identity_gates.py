"""Phase 4B transport independence, identity, and real-team gate checks."""

import copy
import json
from pathlib import Path

import pytest

from police_thief_lab.interop.artifacts import (
    consensus_sha256,
    derive_game_ids,
    final_consensus_scope,
)
from police_thief_lab.interop.runtime import UNRESOLVED_GIT_COMMIT, PeerRuntime
from police_thief_lab.models import Role
from tests.support.interop_test_support import profile


def test_protocol_layer_is_transport_endpoint_agnostic(tmp_path: Path) -> None:
    local = PeerRuntime(
        Role.POLICE, profile(), "127.0.0.1", 8801, "http://127.0.0.1:8802/mcp", tmp_path
    )
    public = PeerRuntime(
        Role.POLICE, profile(), "0.0.0.0", 8801, "https://peer.example/mcp", tmp_path
    )
    assert local.profile.bytes() == public.profile.bytes()
    assert type(local.backend) is type(public.backend)
    assert local.receiver.next_step == public.receiver.next_step


def test_advertised_url_propagates_to_role_appropriate_negotiation_identity(tmp_path: Path) -> None:
    url = "https://public.example/mcp"
    runtime = PeerRuntime(
        Role.POLICE,
        profile(),
        "0.0.0.0",
        8801,
        "https://peer.example/mcp",
        tmp_path,
        advertised_url=url,
        group_id="our-group",
        group_name="Our Group",
    )
    identity = runtime.profile.agreement(runtime.role.value, runtime.identity)["identity"]
    assert identity["group_id"] == "our-group"
    assert identity["mcp_servers"] == {"cop": url}
    assert "localhost" not in json.dumps(identity["mcp_servers"]).lower()
    assert "https://peer.example/mcp" not in runtime.profile.bytes().decode()


def test_git_commit_is_opaque_identity_metadata_outside_consensus(tmp_path: Path) -> None:
    exact = " feature/Build 07 \t"
    runtime = PeerRuntime(
        Role.POLICE,
        profile(),
        "127.0.0.1",
        8801,
        "http://127.0.0.1:8802/mcp",
        tmp_path,
        git_commit=exact,
    )
    agreement = runtime.profile.agreement(runtime.role.value, runtime.identity)
    assert agreement["identity"]["github_commit"] == exact
    assert exact not in runtime.profile.bytes().decode()
    assert exact not in json.dumps(runtime.profile.reference_terms())
    baseline_ids = derive_game_ids(runtime.profile.reference_terms(), "alpha", "beta")
    changed = PeerRuntime(
        Role.POLICE,
        profile(),
        "127.0.0.1",
        8801,
        "http://127.0.0.1:8802/mcp",
        tmp_path,
        git_commit="different",
    )
    assert changed.profile.bytes() == runtime.profile.bytes()
    assert changed.profile.sha256 == runtime.profile.sha256
    assert derive_game_ids(changed.profile.reference_terms(), "alpha", "beta") == baseline_ids
    scope = final_consensus_scope(
        "game",
        {"winner_group": "alpha"},
        [
            {
                "sub_game_number": 1,
                "roles": {"alpha": "police", "beta": "thief"},
                "result": "capture",
                "winner_group": "alpha",
                "score": {"alpha": 20, "beta": 5},
                "github_commit": {"alpha": exact, "beta": "different"},
            }
        ],
    )
    without_commits = copy.deepcopy(scope)
    assert consensus_sha256(scope) == consensus_sha256(without_commits)


@pytest.mark.parametrize("commit", [None, "", UNRESOLVED_GIT_COMMIT])
def test_real_team_gate_refuses_unresolved_local_commit_before_listener(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, commit: str | None
) -> None:
    runtime = PeerRuntime(
        Role.THIEF,
        profile(),
        "127.0.0.1",
        8801,
        "http://127.0.0.1:8802/mcp",
        tmp_path,
        git_commit=commit,
        real_team=True,
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
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    runtime = PeerRuntime(
        Role.THIEF,
        profile(),
        "127.0.0.1",
        8801,
        "http://127.0.0.1:8802/mcp",
        tmp_path,
        git_commit="ours-exact",
        real_team=True,
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
    runtime = PeerRuntime(
        Role.THIEF, profile(), "127.0.0.1", 8801, "http://127.0.0.1:8802/mcp", tmp_path
    )
    runtime.state.position = runtime.config.thief_start
    runtime.state.barriers.update(
        {
            type(runtime.state.position)(2, 3),
            type(runtime.state.position)(4, 3),
            type(runtime.state.position)(3, 2),
            type(runtime.state.position)(3, 4),
        }
    )
    assert runtime._boxed_in()
