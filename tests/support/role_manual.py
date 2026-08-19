"""Reusable academic-manual contract for final role repository READMEs."""

from __future__ import annotations

_HEADINGS = (
    "## Role identity",
    "## Install and validate offline",
    "## Local simulator use",
    "## Academic model and FastMCP architecture",
    "## Decision strategy",
    "## Live GUI and verified Replay",
    "## Official repository layout",
    "## Governance and operational limits",
    "## License and credits",
)

COUNTERPART_URLS = {
    "police": "https://github.com/ilyalaz01/police_thief_p2p-thief",
    "thief": "https://github.com/ilyalaz01/police_thief_p2p-police",
}


def assert_complete_role_manual(document: str, role: str) -> None:
    """Assert the official academic/manual boundary for one role root."""
    assert document.startswith(f"# Police-Thief P2P — {role.title()}\n")
    assert all(heading in document for heading in _HEADINGS)
    assert "two separate role repositories" in document
    assert COUNTERPART_URLS[role] in document
    assert "PENDING_HUMAN_APPROVAL" not in document
    assert "Dec-POMDP" in document
    assert "FastMCP" in document
    assert "Gatekeeper" in document
    assert "Verified OK" in document
    assert "not authorization" in document.lower()
