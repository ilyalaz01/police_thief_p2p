"""Freshness contract for the live guideline-compliance ledger."""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
MATRIX_PATH = ROOT / "docs/GUIDELINES_COMPLIANCE_MATRIX.md"
TODO_PATH = ROOT / "docs/TODO.md"
D12B_AUDIT_PATH = ROOT / "docs/audits/phase4d12b_role_readme_assembly.json"


def matrix() -> str:
    """Read the live compliance matrix."""
    return MATRIX_PATH.read_text(encoding="utf-8")


def row(label: str) -> str:
    """Return one exact Markdown-table row by first-column label."""
    prefix = f"| {label} |"
    return next(line for line in matrix().splitlines() if line.startswith(prefix))


def test_matrix_has_no_known_stale_pre_d12b_claims() -> None:
    document = matrix()
    stale_claims = (
        "18 accepted first-parent PR merges",
        "through Phase 4D11",
        "across 98 files",
        "Multiple technical/research/operations gaps remain",
        "role-specific academic copies remain a separate official-submission task",
    )
    assert not [claim for claim in stale_claims if claim in document]


def test_current_d12b_evidence_is_reflected_without_volatile_counts() -> None:
    audit = json.loads(D12B_AUDIT_PATH.read_text(encoding="utf-8"))
    coverage = audit["validation"]["combined_coverage_percent"]
    document = matrix()
    assert f"{coverage:.2f}%" in document
    assert "Phase 4D12B" in row("1 README")
    assert "through current accepted `main`" in row("7 Git branches/commits/PRs/tags")
    assert "through the current accepted phase" in row("7 Prompt log")


def test_partial_status_is_honest_history_not_an_open_technical_gap() -> None:
    document = matrix()
    normalized = " ".join(document.split())
    assert "no `MISSING` generic-guideline row remains" in normalized
    assert "historical evidence cannot be reconstructed" in normalized
    assert "higher-authority submission" in normalized
    assert "human operations" in normalized
    assert "| MISSING |" not in document
    assert "shared technical checklist is implemented" in row("16 Final checklist")


def test_live_todo_keeps_official_delivery_work_explicit() -> None:
    statuses = re.findall(r"Status: (DONE|IN_PROGRESS|PLANNED|BLOCKED)", TODO_PATH.read_text())
    assert statuses.count("DONE") == 21
    assert statuses.count("IN_PROGRESS") == 3
    assert statuses.count("BLOCKED") == 1
    assert statuses.count("PLANNED") == 0
