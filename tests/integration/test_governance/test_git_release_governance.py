"""Regression contract for inspectable Git and release governance."""

from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
AUDIT_PATH = PROJECT_ROOT / "docs/audits/phase4d11_git_release_governance.json"
BASELINE_COMMIT = "96d3878ed1ac3776810284be7c23315ba3ad53e1"
PARTNER_EMAIL = "ndvp39@gmail.com"


def git(*args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    """Run Git against this checkout with deterministic text decoding."""
    return subprocess.run(
        [
            "git",
            "-c",
            f"safe.directory={PROJECT_ROOT.as_posix()}",
            "-C",
            str(PROJECT_ROOT),
            *args,
        ],
        check=check,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )


def load_audit() -> dict[str, object]:
    """Load the retained machine-readable governance evidence."""
    return json.loads(AUDIT_PATH.read_text(encoding="utf-8"))


def test_ci_checkout_preserves_history_and_tags() -> None:
    workflow = (PROJECT_ROOT / ".github/workflows/quality-gate.yml").read_text(
        encoding="utf-8"
    )
    assert "fetch-depth: 0" in workflow
    assert "submodules: recursive" in workflow
    assert "persist-credentials: false" in workflow


def test_annotated_baseline_tag_is_real_and_unchanged() -> None:
    assert git("cat-file", "-t", "team-baseline-v1").stdout.strip() == "tag"
    assert git("rev-parse", "team-baseline-v1^{}").stdout.strip() == BASELINE_COMMIT


def test_accepted_history_contains_pr_and_partner_evidence() -> None:
    subjects = git("log", "--first-parent", "--merges", "--format=%s", "HEAD")
    pr_numbers = {
        int(match.group(1))
        for subject in subjects.stdout.splitlines()
        if (match := re.match(r"Merge (?:PR|pull request) #(\d+)", subject))
    }
    emails = git("log", "--format=%ae", "HEAD").stdout.splitlines()
    assert len(pr_numbers) >= 18
    assert emails.count(PARTNER_EMAIL) >= 8


def test_retained_audit_matches_the_inspectable_cutoff() -> None:
    audit = load_audit()
    history = audit["history"]
    assert audit["status"] == "GREEN"
    assert history["accepted_pr_merge_count"] == 18
    assert history["accepted_partner_commit_count"] == 8
    assert git("merge-base", "--is-ancestor", history["cutoff_commit"], "HEAD").returncode == 0
    assert history["baseline_tag_target"] == BASELINE_COMMIT


def test_final_submission_tag_remains_human_gated() -> None:
    audit = load_audit()
    assert git("tag", "--list", "v1.0-submission").stdout == ""
    assert audit["final_submission_tag"]["state"] == "ABSENT_PENDING_SUB_001"
    todo = (PROJECT_ROOT / "docs/TODO.md").read_text(encoding="utf-8")
    assert "## GIT-001" in todo and "Status: DONE" in todo
    assert "## SUB-001" in todo and "Status: PLANNED" in todo
