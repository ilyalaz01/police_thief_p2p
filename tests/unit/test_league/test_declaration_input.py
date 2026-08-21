"""Loading one operator declaration file into the validated identity type."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from police_thief_lab.league.declaration_input import load_declaration_identity
from tests.support.league_fixtures import GROUP_A

VALID = {
    "group_id": GROUP_A,
    "group_name": "Alpha Team",
    "members": ["Student One", "Student Two"],
    "cop_repo": "https://github.com/example/cop",
    "thief_repo": "https://github.com/example/thief",
    "cop_mcp_url": "https://cop.example/mcp",
    "thief_mcp_url": "https://thief.example/mcp",
    "llm_model": "deterministic-python",
    "hardware": {
        "cpu_type": "Intel i5",
        "cpu_freq_mhz": 2500,
        "cpu_cores": 10,
        "ram_gb": 32,
        "gpu_model": "GTX 1070",
        "vram_gb": 8,
    },
}


def _write(tmp_path: Path, value: object) -> Path:
    """Write one candidate declaration document and return its path."""
    path = tmp_path / "declaration.json"
    path.write_text(json.dumps(value, ensure_ascii=False), encoding="utf-8")
    return path


def test_a_complete_declaration_maps_to_the_builder_identity_shape(tmp_path: Path) -> None:
    identity = load_declaration_identity(_write(tmp_path, VALID)).object()
    assert identity["group_id"] == GROUP_A
    assert identity["members"] == ["Student One", "Student Two"]
    assert identity["repos"]["thief"] == "https://github.com/example/thief"
    assert identity["spec"]["gpu_type"] == "GTX 1070"
    assert identity["spec"]["ram_gb"] == 32


def test_every_missing_top_level_value_is_reported_at_once(tmp_path: Path) -> None:
    incomplete = {key: value for key, value in VALID.items() if key not in ("members", "llm_model")}
    with pytest.raises(ValueError, match="declaration file is missing"):
        load_declaration_identity(_write(tmp_path, incomplete))


def test_an_unfilled_hardware_number_blocks_the_declaration(tmp_path: Path) -> None:
    unfilled = dict(VALID, hardware=dict(VALID["hardware"], vram_gb=None))
    with pytest.raises(ValueError, match="declaration hardware is missing"):
        load_declaration_identity(_write(tmp_path, unfilled))


def test_a_non_object_document_is_refused(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="one JSON object"):
        load_declaration_identity(_write(tmp_path, [VALID]))


def test_members_must_be_a_list_of_names(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="members must be a JSON array"):
        load_declaration_identity(_write(tmp_path, dict(VALID, members="Student One")))


def test_declaration_validation_still_applies_after_loading(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="group_id"):
        load_declaration_identity(_write(tmp_path, dict(VALID, group_id="too-short")))
