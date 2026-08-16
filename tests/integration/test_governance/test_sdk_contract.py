"""Characterization contract for the single public SDK entry point."""

from __future__ import annotations

import ast

from police_thief_lab import PoliceThiefSDK
from police_thief_lab.evaluation import cross_play
from police_thief_lab.interop.artifacts import build_result
from police_thief_lab.interop.crypto import hcommit
from police_thief_lab.interop.runtime import run_peer
from police_thief_lab.policies import ScentTacticalPolice
from police_thief_lab.rules import legal_actions
from tests.support.project_paths import PROJECT_ROOT

ROOT = PROJECT_ROOT

EXPECTED = {
    "domain": {
        "Action", "Barrier", "GameConfig", "Position", "Role", "Simulator", "WorldState",
        "legal_actions", "replay", "score_for", "scent_model_for", "validate_action",
    },
    "policies": {
        "BarrierAwareThief", "BeliefSearchPolice", "DeterministicSearchPolice",
        "PartitionPolice", "RandomLegalPolice", "RandomLegalThief", "ScentGreedyPolice",
        "ScentTacticalPolice", "SpaceSeekingThief", "TrajectoryBeamBelief",
    },
    "evaluation": {
        "AblatedBackend", "BatchResult", "GameResult", "ScentAblation", "cross_play",
        "markdown_matrix", "run_batch", "run_game", "write_json",
    },
    "artifacts": {
        "aggregate_scores", "build_config_artifact", "build_declaration", "build_log",
        "build_result", "canonical_json", "canonical_sha256", "consensus_sha256",
        "derive_game_ids", "final_consensus_scope", "hcommit", "replay_sequence", "seal",
        "verify_audit", "verify_records", "write_artifacts", "write_reference_v3_artifacts",
    },
    "transport": {
        "ApiGatekeeper", "EndpointConfig", "MatchProfile", "McpPeerClient", "PeerInboxes",
        "PeerRuntime",
        "TurnInbox", "TurnMessage", "action_to_wire", "build_server", "config_from_profile",
        "discover_tools", "launch_peer", "redact_secrets", "redact_url", "run_peer",
        "start_server", "validate_mcp_url",
    },
    "configuration": {
        "OperationalConfig", "load_operational_config", "scan_configuration_secrets",
    },
}


def test_sdk_exposes_the_approved_business_operation_inventory() -> None:
    sdk = PoliceThiefSDK()
    for service, expected in EXPECTED.items():
        actual = {name for name in dir(getattr(sdk, service)) if not name.startswith("_")}
        assert expected <= actual, (service, sorted(expected - actual))


def test_sdk_aliases_preserve_existing_function_and_policy_contracts() -> None:
    sdk = PoliceThiefSDK()
    assert sdk.domain.legal_actions is legal_actions
    assert sdk.policies.ScentTacticalPolice is ScentTacticalPolice
    assert sdk.evaluation.cross_play is cross_play
    assert sdk.artifacts.build_result is build_result
    assert sdk.artifacts.hcommit is hcommit
    assert sdk.transport.run_peer is run_peer


def test_executable_project_consumers_import_only_the_root_sdk() -> None:
    consumers = sorted((ROOT / "experiments").glob("*.py"))
    violations = []
    for path in consumers:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and (node.module or "").startswith(
                "police_thief_lab"
            ):
                imported = {alias.name for alias in node.names}
                if node.module != "police_thief_lab" or imported != {"PoliceThiefSDK"}:
                    violations.append(f"{path.relative_to(ROOT)}:{node.lineno}")
    assert violations == []


def test_cli_imports_the_sdk_layer_instead_of_business_modules() -> None:
    path = ROOT / "src/police_thief_lab/peer_cli.py"
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    relative_modules = {
        node.module
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.level
    }
    assert relative_modules == {"sdk"}
