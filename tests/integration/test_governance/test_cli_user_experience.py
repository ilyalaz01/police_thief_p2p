"""User-facing CLI and manual contracts for the offline-safe entry point."""

from __future__ import annotations

from police_thief_lab import peer_cli
from tests.support.project_paths import PROJECT_ROOT


def _read(relative: str) -> str:
    """Read one tracked UTF-8 documentation file."""
    return (PROJECT_ROOT / relative).read_text(encoding="utf-8")


def test_peer_help_explains_every_option_and_authorization_boundary() -> None:
    """Keep every accepted peer option discoverable without starting a peer."""
    help_text = peer_cli.build_parser().format_help()
    options = (
        "--role",
        "--operational-config",
        "--profile",
        "--host",
        "--port",
        "--advertised-url",
        "--group-id",
        "--group-name",
        "--git-commit",
        "--real-team",
        "--opponent-url",
        "--public",
        "--artifacts",
        "--output",
        "--seed",
    )
    assert all(option in help_text for option in options)
    assert "starts one independent peer process" in help_text
    assert "does not authorize" in help_text
    assert "counted" in help_text


def test_peer_parser_retains_safe_defaults() -> None:
    """Help improvements must not change established startup defaults."""
    args = peer_cli.build_parser().parse_args(
        [
            "--role",
            "police",
            "--profile",
            "profile.json",
            "--port",
            "8801",
            "--opponent-url",
            "http://127.0.0.1:8802/mcp",
            "--artifacts",
            "artifacts",
            "--output",
            "result.json",
        ]
    )
    assert (args.host, args.seed, args.public, args.real_team) == ("127.0.0.1", 1, False, False)
    assert args.operational_config is None


def test_readme_is_a_complete_current_user_manual() -> None:
    """Guard the manual sections required by DOC-001."""
    readme = _read("README.md")
    headings = (
        "## Requirements",
        "## Installation",
        "## Offline quick start",
        "## Peer CLI reference",
        "## Operational modes and authorization",
        "## Configuration",
        "## Outputs and artifacts",
        "## Troubleshooting",
        "## Contributing",
        "## License and credits",
        "## Submission-readiness limits",
    )
    assert all(heading in readme for heading in headings)
    assert all(option in readme for option in ("--role", "--profile", "--real-team", "--public"))
    assert "two separate role repositories" in readme
    assert "Live GUI" in readme and "Replay" in readme
    assert "does not authorize" in readme


def test_submission_readiness_keeps_official_and_human_blockers_visible() -> None:
    """Do not let guideline cleanup hide higher-authority submission gaps."""
    readiness = _read("docs/OFFICIAL_SUBMISSION_READINESS.md")
    required = (
        "Rule 49",
        "two separate GitHub repositories",
        "Live GUI",
        "Replay",
        "v1.0-submission",
        "two different opponent teams",
        "Gmail API",
        "BLOCKED",
    )
    assert all(term in readiness for term in required)
