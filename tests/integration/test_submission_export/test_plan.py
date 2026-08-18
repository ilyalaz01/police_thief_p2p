"""Tests for the deterministic plan operation."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from tools.submission_export.planner import plan

pytestmark = pytest.mark.integration


def test_valid_police_plan_returns_correct_schema(
    police_manifest: dict, repo_root: Path
) -> None:
    result = plan(police_manifest, repo_root)
    assert result["schema"] == "submission_export_plan_v1"
    assert result["role"] == "police"


def test_valid_thief_plan_returns_correct_schema(
    thief_manifest: dict, repo_root: Path
) -> None:
    result = plan(thief_manifest, repo_root)
    assert result["schema"] == "submission_export_plan_v1"
    assert result["role"] == "thief"


def test_plan_is_deterministic_across_repeated_runs(
    police_manifest: dict, repo_root: Path
) -> None:
    first = json.dumps(plan(police_manifest, repo_root), sort_keys=True)
    second = json.dumps(plan(police_manifest, repo_root), sort_keys=True)
    assert first == second


def test_plan_byte_identical_json(police_manifest: dict, repo_root: Path) -> None:
    a = json.dumps(plan(police_manifest, repo_root), sort_keys=True, indent=2)
    b = json.dumps(plan(police_manifest, repo_root), sort_keys=True, indent=2)
    assert a == b


def test_files_are_sorted_in_plan(police_manifest: dict, repo_root: Path) -> None:
    result = plan(police_manifest, repo_root)
    paths = [e["path"] for e in result["files"]]
    assert paths == sorted(paths)


def test_stable_ordering_regardless_of_input_order(
    police_manifest: dict, repo_root: Path
) -> None:
    fwd = dict(police_manifest, include=sorted(police_manifest["include"]))
    rev = dict(police_manifest, include=sorted(police_manifest["include"], reverse=True))
    assert json.dumps(plan(fwd, repo_root), sort_keys=True) == json.dumps(
        plan(rev, repo_root), sort_keys=True
    )


def test_each_file_has_64char_sha256(police_manifest: dict, repo_root: Path) -> None:
    result = plan(police_manifest, repo_root)
    for entry in result["files"]:
        assert "sha256" in entry
        assert len(entry["sha256"]) == 64
        assert all(c in "0123456789abcdef" for c in entry["sha256"])


def test_aggregate_hash_is_present_and_64chars(
    police_manifest: dict, repo_root: Path
) -> None:
    result = plan(police_manifest, repo_root)
    assert "aggregate_hash" in result
    assert len(result["aggregate_hash"]) == 64


def test_counterpart_url_preserved_verbatim(
    police_manifest: dict, repo_root: Path
) -> None:
    result = plan(police_manifest, repo_root)
    assert result["counterpart_repository_url"] == "PENDING_HUMAN_APPROVAL"


def test_source_commit_carried_through(police_manifest: dict, repo_root: Path) -> None:
    result = plan(police_manifest, repo_root)
    assert result["source_commit"] == police_manifest["source_commit"]


def test_plan_output_contains_no_absolute_source_path(
    police_manifest: dict, repo_root: Path
) -> None:
    result_str = json.dumps(plan(police_manifest, repo_root))
    posix_root = repo_root.as_posix()
    assert posix_root not in result_str
