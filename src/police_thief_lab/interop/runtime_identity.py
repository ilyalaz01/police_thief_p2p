"""Peer negotiation identity assembled from operator declaration input."""

from __future__ import annotations

from typing import Any

LOCAL_REPOSITORY = "local-unpublished"


def _self_test_identity(role_value: str, group_id: str | None, group_name: str | None) -> dict:
    """Return the historical self-test identity used when no declaration is supplied."""
    return {
        "group_id": group_id or f"local-{role_value}",
        "group_name": group_name or f"Local {role_value.title()}",
        "members": [],
        "repos": {"cop": LOCAL_REPOSITORY, "thief": LOCAL_REPOSITORY},
        "llm_model": "deterministic-python",
        "spec": {},
    }


def _declared_identity(
    declaration: dict[str, Any], group_id: str | None, group_name: str | None
) -> dict[str, Any]:
    """Return the declared identity, refusing a conflicting command-line override."""
    identity = dict(declaration)
    for field, supplied in (("group_id", group_id), ("group_name", group_name)):
        if supplied is not None and supplied != identity.get(field):
            raise ValueError(
                f"declared {field} and the supplied {field} differ; resolve them explicitly"
            )
    return identity


def peer_identity_object(
    role_value: str,
    advertised_url: str,
    git_commit: str,
    group_id: str | None = None,
    group_name: str | None = None,
    declaration: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build one negotiation identity without inventing any operator-supplied value."""
    role_key = "cop" if role_value == "police" else "thief"
    if declaration is None:
        identity = _self_test_identity(role_value, group_id, group_name)
        servers: dict[str, Any] = {}
    else:
        identity = _declared_identity(declaration, group_id, group_name)
        servers = dict(identity.get("mcp_servers", {}))
    servers[role_key] = advertised_url
    identity["mcp_servers"] = servers
    identity["github_commit"] = git_commit
    return identity


def validate_hint(hint: str, max_words: int) -> str:
    """Reject a hint longer than the negotiated word cap before it reaches the wire."""
    if len(hint.split()) > max_words:
        raise ValueError(f"hint exceeds the negotiated {max_words}-word cap")
    return hint
