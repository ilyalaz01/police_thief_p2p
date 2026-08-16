"""The CI workflow must be a thin wrapper over the documented local command.

No YAML parser is added as a dependency (out of this workstream's module
boundary to add); the workflow text is checked directly instead.
"""

from __future__ import annotations

from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
_WORKFLOW = _REPO_ROOT / ".github" / "workflows" / "quality-gate.yml"
_LOCAL_ENTRY_POINT = "uv run python -m tools.offline_ops.cli quality-gate"


def _workflow_text() -> str:
    return _WORKFLOW.read_text(encoding="utf-8")


def test_workflow_file_exists() -> None:
    assert _WORKFLOW.is_file()


def test_workflow_invokes_the_documented_local_entry_point() -> None:
    assert _LOCAL_ENTRY_POINT in _workflow_text()


def test_workflow_docs_agree_on_the_entry_point() -> None:
    docs = (_REPO_ROOT / "docs" / "RELEASE_ENGINEERING.md").read_text(encoding="utf-8")
    assert _LOCAL_ENTRY_POINT in docs


def test_workflow_uses_read_only_contents_permission() -> None:
    text = _workflow_text()
    assert "permissions:" in text
    assert "contents: read" in text


def test_workflow_uses_no_repository_secrets() -> None:
    assert "secrets." not in _workflow_text()


def test_workflow_pins_actions_by_commit_sha() -> None:
    text = _workflow_text()
    for action in ("actions/checkout@", "astral-sh/setup-uv@"):
        line = next(line for line in text.splitlines() if action in line)
        sha = line.split("@", 1)[1].split()[0]
        assert len(sha) == 40 and all(c in "0123456789abcdef" for c in sha)


def test_workflow_uploads_no_artifact() -> None:
    assert "upload-artifact" not in _workflow_text()


def test_workflow_does_not_reimplement_the_gate() -> None:
    text = _workflow_text()
    for forbidden in ("pytest ", "ruff check", "verify_vectors.py"):
        assert forbidden not in text
