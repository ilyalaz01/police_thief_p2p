"""Cross-document freshness checks derived from the official delivery rules."""

from __future__ import annotations

import json
import re

from tests.support.project_paths import PROJECT_ROOT
from tests.support.role_manual import COUNTERPART_URLS

ROOT = PROJECT_ROOT
ROLE_READMES = {
    "police": "submission/templates/police/README.md",
    "thief": "submission/templates/thief/README.md",
}
PUBLICATION_AUDIT = ROOT / "docs/audits/phase4d14e_role_publication.json"


def read(relative: str) -> str:
    """Read one living project document."""
    return (ROOT / relative).read_text(encoding="utf-8")


def test_living_prds_do_not_describe_completed_controls_as_planned() -> None:
    """Dedicated PRDs must agree with accepted implementation evidence."""
    documents = "\n".join(
        read(path)
        for path in (
            "docs/PRD_GAME_CORE_AND_OBSERVABILITY.md",
            "docs/PRD_P2P_INTEROPERABILITY.md",
            "docs/PRD_AUDIT_REPLAY.md",
            "docs/PRD_RELEASE_ENGINEERING.md",
        )
    )
    stale = (
        "documentation/refactoring coverage remains planned",
        "Rate limiting, bounded queue depth, backpressure, drain policy, and call monitoring "
        "are not implemented",
        "Unresolved: offline redacted validation/reporting and broader security review",
        "Status: **PLANNED**; no implementation exists",
    )
    assert not [claim for claim in stale if claim in documents]


def test_adr_index_status_matches_each_record() -> None:
    """The ADR index may not disagree with the status inside a record."""
    index = read("docs/adr/README.md")
    indexed = dict(re.findall(r"\[(ADR-\d{3})\].*— (\w+)$", index, re.MULTILINE))
    actual = {}
    for path in sorted((ROOT / "docs/adr").glob("ADR-*.md")):
        status = re.search(r"^Status: (\w+)$", path.read_text(encoding="utf-8"), re.MULTILINE)
        assert status
        actual[path.name[:7]] = status.group(1)
    assert indexed == actual


def test_role_readmes_cover_the_official_academic_report() -> None:
    """Future root READMEs must carry the Chapter-9 academic-report evidence."""
    required = (
        "Dec-POMDP",
        "FastMCP",
        "Gatekeeper",
        "## Decision strategy",
        "No reinforcement learning",
        "docs/images/live-gui-local-truth.jpg",
        "docs/images/replay-verified-ok.jpg",
        "Verified OK",
    )
    for role, path in ROLE_READMES.items():
        document = read(path)
        assert not [term for term in required if term not in document]
        assert COUNTERPART_URLS[role] in document
        assert "PENDING_HUMAN_APPROVAL" not in document
    for image in (
        "docs/images/live-gui-local-truth.jpg",
        "docs/images/replay-verified-ok.jpg",
    ):
        assert (ROOT / image).is_file()


def test_open_official_delivery_implementation_is_not_hidden_as_human_only() -> None:
    """Technical gaps must stay distinct from authorization and bilateral gates."""
    todo = read("docs/TODO.md")
    readiness = read("docs/OFFICIAL_SUBMISSION_READINESS.md")
    decisions = read("docs/INTEROP_DECISIONS.md")
    for task_id in ("LGE-001", "MAIL-001"):
        assert f"## {task_id}" in todo
    for phrase in (
        "six-sub-game series",
        "full Appendix-B shared configuration",
        "Gmail API sender is not implemented",
        "eight-character group ID",
    ):
        assert phrase in readiness
    assert "UNRESOLVED_FOR_COUNTED_SERIES" in decisions


def test_iso_assessment_avoids_obsolete_fixed_suite_evidence() -> None:
    """The living ISO assessment must not freeze superseded run counts."""
    document = read("docs/ISO_IEC_25010_ASSESSMENT.md")
    assert "312 deterministic offline tests" not in document
    assert "92.51% branch coverage" not in document
    assert "once `CON-001` capacity measurements are collected" not in document


def test_public_role_repositories_have_exact_green_evidence_without_final_tags() -> None:
    """Rule 49/50 publication must be exact while later operations stay blocked."""
    audit = json.loads(PUBLICATION_AUDIT.read_text(encoding="utf-8"))
    assert audit["status"] == "GREEN_PUBLIC_ROLE_REPOSITORIES"
    expected = {
        "police": (
            "https://github.com/ilyalaz01/police_thief_p2p-police",
            "42c5367d690abda6b01c6aa91499491526123ed8",
            "https://github.com/ilyalaz01/police_thief_p2p-police/actions/runs/32230351200",
        ),
        "thief": (
            "https://github.com/ilyalaz01/police_thief_p2p-thief",
            "f279dc2c736df1b234f857de6e085e38fbdb73f1",
            "https://github.com/ilyalaz01/police_thief_p2p-thief/actions/runs/32230359324",
        ),
    }
    for role, (url, commit, run_url) in expected.items():
        evidence = audit["repositories"][role]
        assert (evidence["url"], evidence["commit"]) == (url, commit)
        assert evidence["public_ci"] == {"status": "PASS", "run_url": run_url}
    assert audit["published_historical_tags"] == ["team-baseline-v1"]
    assert audit["final_submission_tags_created"] is False
    assert not any(audit["external_operations_authorized"].values())

    readiness = read("docs/OFFICIAL_SUBMISSION_READINESS.md")
    for requirement in ("Rule 49:", "Rule 50:"):
        row = next(line for line in readiness.splitlines() if line.startswith(f"| {requirement}"))
        assert "| DONE |" in row
