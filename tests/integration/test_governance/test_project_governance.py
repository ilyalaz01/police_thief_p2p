"""Regression checks for the retrospective project-governance baseline."""

from __future__ import annotations

import json
import re

from tests.support.project_paths import PROJECT_ROOT

ROOT = PROJECT_ROOT
NOTICE_LINES = (
    "Retrospective baseline created after the validated prototype.",
    "These documents did not exist before the prototype and do not claim otherwise.",
)
DOCS = {
    "docs/PRD.md",
    "docs/PLAN.md",
    "docs/TODO.md",
    "docs/GUIDELINES_COMPLIANCE_MATRIX.md",
    "docs/QUALITY_PLAN.md",
    "docs/QUALITY_CRITICAL_PATHS.md",
    "docs/CONCURRENCY_AND_CAPACITY.md",
    "docs/OFFICIAL_SUBMISSION_READINESS.md",
    "docs/TESTING.md",
    "docs/PROMPT_ENGINEERING_LOG.md",
    "docs/PRD_GAME_CORE_AND_OBSERVABILITY.md",
    "docs/PRD_POLICY_EVALUATION.md",
    "docs/PRD_P2P_INTEROPERABILITY.md",
    "docs/PRD_AUDIT_REPLAY.md",
    "docs/PRD_ARTIFACTS_AND_CONSENSUS.md",
    "docs/PRD_RELEASE_ENGINEERING.md",
    "docs/adr/README.md",
    "docs/audits/PHASE4D0_GUIDELINES_RECOVERY.md",
    "docs/audits/PHASE4D3_TEST_QUALITY.md",
    "docs/audits/PHASE4D4_CONCURRENCY_LIFECYCLE.md",
}
ALLOWED_TASK = {"DONE", "IN_PROGRESS", "PLANNED", "BLOCKED"}
ALLOWED_ADR = {"PROPOSED", "ACCEPTED", "SUPERSEDED", "REJECTED"}
GAP_STATUSES = {"PARTIAL", "MISSING", "BLOCKED_BY_HIGHER_AUTHORITY"}
LIVE_DOCUMENTS = DOCS - {
    "docs/adr/README.md",
    "docs/audits/PHASE4D0_GUIDELINES_RECOVERY.md",
}


def read(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


def test_mandatory_documents_json_and_notice() -> None:
    assert all((ROOT / path).is_file() for path in DOCS)
    audit = json.loads(read("docs/audits/phase4d0_guidelines_recovery.json"))
    assert audit["phase"] == "4D0"
    assert audit["retrospective_status"] == "RETROSPECTIVE_AFTER_VALIDATED_PROTOTYPE"
    for path in DOCS - {"docs/adr/README.md", "docs/audits/PHASE4D0_GUIDELINES_RECOVERY.md"}:
        assert all(line in read(path) for line in NOTICE_LINES)


def test_todo_status_evidence_and_definition_of_done() -> None:
    text = read("docs/TODO.md")
    sections = re.split(r"(?=^## [A-Z]+-\d{3} )", text, flags=re.MULTILINE)[1:]
    assert sections
    for section in sections:
        status = re.search(r"Status: (\w+)", section)
        assert status and status.group(1) in ALLOWED_TASK
        assert "Definition of Done:" in section
        assert "Validation commands:" in section
        if status.group(1) == "DONE":
            evidence = re.search(r"Evidence: (.+)", section)
            assert evidence and "not applicable" not in evidence.group(1).lower()


def test_every_matrix_gap_links_to_a_todo_task() -> None:
    todo_ids = set(re.findall(r"^## ([A-Z]+-\d{3}) ", read("docs/TODO.md"), re.MULTILINE))
    rows = [line for line in read("docs/GUIDELINES_COMPLIANCE_MATRIX.md").splitlines()
            if line.startswith("|")]
    for row in rows:
        cells = [cell.strip() for cell in row.strip("|").split("|")]
        if len(cells) >= 5 and cells[1] in GAP_STATUSES:
            assert cells[4] in todo_ids, row


def test_adr_statuses_and_required_mermaid_diagrams() -> None:
    adrs = sorted((ROOT / "docs/adr").glob("ADR-*.md"))
    assert len(adrs) == 6
    for adr in adrs:
        match = re.search(r"^Status: (\w+)$", adr.read_text(encoding="utf-8"), re.MULTILINE)
        assert match and match.group(1) in ALLOWED_ADR
    plan = read("docs/PLAN.md")
    assert plan.count("```mermaid") >= 6
    for label in ("System context", "Containers/processes", "Main components",
                  "Deployment topology", "Complete P2P turn", "Commit-reveal audit",
                  "Artifact-generation flow"):
        assert label in plan


def test_no_fabricated_history_private_body_or_personalized_handoff() -> None:
    new_text = "\n".join(read(path) for path in DOCS | {"README.md"})
    forbidden = (
        "PRD existed before", "PLAN existed before", "TODO existed before",
        "historical prompt transcript", "Dear " + "opponent", "handoff to our " + "partner",
        "PRIVATE_SOURCE_BODY", "copied professor implementation body",
    )
    assert not any(term.lower() in new_text.lower() for term in forbidden)
    assert "No complete historical prompt log existed" in new_text


def test_readme_markdown_links_resolve_locally() -> None:
    readme = read("README.md")
    links = re.findall(r"\[[^]]+\]\(([^)]+)\)", readme)
    local = [target.split("#", 1)[0] for target in links if "://" not in target]
    assert local
    assert all((ROOT / target).exists() for target in local)


def test_live_documented_test_paths_exist() -> None:
    references = {
        match
        for path in LIVE_DOCUMENTS
        for match in re.findall(
            r"`((?:tests/)?(?:[A-Za-z0-9_.-]+/)*test_[A-Za-z0-9_.-]+\.py)`",
            read(path),
        )
    }
    assert references
    missing = sorted(
        reference
        for reference in references
        if not (
            ROOT / (reference if reference.startswith("tests/") else f"tests/{reference}")
        ).is_file()
    )
    assert missing == []


def test_source_and_test_modules_stay_within_150_counted_lines() -> None:
    violations = {}
    for directory in (ROOT / "src", ROOT / "tests"):
        for path in directory.rglob("*.py"):
            counted = sum(
                bool(line.strip()) and not line.lstrip().startswith("#")
                for line in path.read_text(encoding="utf-8").splitlines()
            )
            if counted > 150:
                violations[path.relative_to(ROOT).as_posix()] = counted
    assert violations == {}
