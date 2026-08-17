"""Contracts for the public-safe Phase 4D9 sensitivity publication."""

from __future__ import annotations

import ast
import hashlib
import importlib
import json
import xml.etree.ElementTree as ET
from pathlib import Path

from tests.support.project_paths import PROJECT_ROOT

ROOT = PROJECT_ROOT
DESIGN = ROOT / "data/research/sensitivity_design.v1.json"
OUTPUTS = {
    "raw": "results/research/phase4d9_sensitivity.json",
    "summary": "results/research/phase4d9_summary.csv",
    "board_figure": "assets/research/capture_by_board_size.svg",
    "survival_figure": "assets/research/capture_by_survival_threshold.svg",
    "notebook": "notebooks/POLICY_SENSITIVITY_ANALYSIS.md",
}
MANIFEST = ROOT / "results/research/phase4d9_manifest.json"


def _sha(path: Path) -> str:
    """Return one file's SHA-256 digest."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_design_was_predeclared_as_a_bounded_local_experiment() -> None:
    design = json.loads(DESIGN.read_text(encoding="utf-8"))
    assert design["status"] == "PREDECLARED_BEFORE_FIRST_RUN"
    assert design["operation_class"] == "LOCAL_SIMULATOR_EXPERIMENT"
    assert design["method"]["name"] == "paired_one_factor_at_a_time_screening"
    assert design["method"]["global_sensitivity_claimed"] is False
    assert design["factors"] == {
        "board_size": [7, 9, 11], "survival_threshold": [35, 50, 70]
    }
    assert design["seeds"] == {"start": 0, "stop_exclusive": 40}
    assert len(design["settings"]) == 5
    assert len(design["scenarios"]) == 3
    assert design["expected_games"] == 2400
    assert design["policies"]["frozen_champion"] == "ScentTacticalPolice"


def test_research_code_uses_only_the_public_sdk_and_short_documented_files() -> None:
    files = sorted((ROOT / "tools/research").glob("*.py"))
    assert files
    violations: list[str] = []
    for path in files:
        text = path.read_text(encoding="utf-8")
        tree = ast.parse(text)
        assert ast.get_docstring(tree)
        counted = sum(
            bool(line.strip()) and not line.lstrip().startswith("#")
            for line in text.splitlines()
        )
        if counted > 150:
            violations.append(f"{path.name}:{counted}")
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and (node.module or "").startswith(
                "police_thief_lab."
            ):
                violations.append(f"{path.name}:{node.lineno}:internal_import")
    assert violations == []
    assert "PoliceThiefSDK" in "".join(path.read_text(encoding="utf-8") for path in files)
    assert "WorldState" not in "".join(path.read_text(encoding="utf-8") for path in files)


def test_committed_publication_matches_manifest_and_reproduction(tmp_path: Path) -> None:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    for key, relative in OUTPUTS.items():
        assert _sha(ROOT / relative) == manifest["artifacts"][key]["sha256"]
    publication = importlib.import_module("tools.research.publication")
    regenerated = publication.build_publication(DESIGN, tmp_path)
    assert regenerated["artifacts"] == manifest["artifacts"]
    for key, relative in OUTPUTS.items():
        assert (tmp_path / relative).read_bytes() == (ROOT / relative).read_bytes(), key


def test_raw_rows_and_summary_are_complete_and_role_safe() -> None:
    payload = json.loads((ROOT / OUTPUTS["raw"]).read_text(encoding="utf-8"))
    assert payload["operation_class"] == "LOCAL_SIMULATOR_EXPERIMENT"
    assert payload["record_count"] == 2400 == len(payload["records"])
    assert len(payload["summary"]) == 20
    assert len(payload["effects"]) == 16
    encoded = json.dumps(payload, sort_keys=True).lower()
    for forbidden in ("opponent_position", "worldstate", "nonce", "opponent_url", "token"):
        assert forbidden not in encoded
    assert sum(row["illegal_actions"] for row in payload["records"]) == 0


def test_figures_and_analysis_are_accessible_and_honest() -> None:
    for key in ("board_figure", "survival_figure"):
        root = ET.parse(ROOT / OUTPUTS[key]).getroot()
        assert root.attrib["width"] == "1200"
        assert root.attrib["height"] == "700"
        assert root.find("{http://www.w3.org/2000/svg}title") is not None
        assert root.find("{http://www.w3.org/2000/svg}desc") is not None
    notebook = (ROOT / OUTPUTS["notebook"]).read_text(encoding="utf-8")
    for phrase in (
        "Local simulator experiment", "one-factor-at-a-time", "not a Sobol",
        "Wilson 95%", "\\Delta_i", "ScentTacticalPolice remains frozen",
        "10.1080/00401706.1991.10484804", "10.1016/j.cpc.2009.09.018",
        "10.1080/01621459.1927.10502953",
    ):
        assert phrase in notebook
