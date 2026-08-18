"""Tests for fail-closed path security and manifest refusals."""

from __future__ import annotations

from pathlib import Path

import pytest

from tools.submission_export.manifest import ManifestError
from tools.submission_export.path_guard import PathViolationError
from tools.submission_export.planner import plan

pytestmark = pytest.mark.integration


def _plan_with_include(base: dict, include: list[str], repo_root: Path) -> None:
    plan(dict(base, include=include), repo_root)


def test_reject_absolute_path(police_manifest: dict, repo_root: Path) -> None:
    with pytest.raises(PathViolationError):
        _plan_with_include(police_manifest, ["/etc/passwd"], repo_root)


def test_reject_drive_qualified_path(police_manifest: dict, repo_root: Path) -> None:
    with pytest.raises(PathViolationError):
        _plan_with_include(police_manifest, ["C:README.md"], repo_root)


def test_reject_dotdot_component(police_manifest: dict, repo_root: Path) -> None:
    with pytest.raises(PathViolationError):
        _plan_with_include(police_manifest, ["../outside.txt"], repo_root)


def test_reject_empty_path(police_manifest: dict, repo_root: Path) -> None:
    with pytest.raises(PathViolationError):
        _plan_with_include(police_manifest, [""], repo_root)


def test_reject_backslash_path(police_manifest: dict, repo_root: Path) -> None:
    with pytest.raises(PathViolationError):
        _plan_with_include(police_manifest, ["docs\\PRD.md"], repo_root)


def test_reject_duplicate_paths(police_manifest: dict, repo_root: Path) -> None:
    with pytest.raises(PathViolationError):
        _plan_with_include(police_manifest, ["README.md", "README.md"], repo_root)


def test_reject_case_insensitive_collision(
    police_manifest: dict, repo_root: Path
) -> None:
    with pytest.raises(PathViolationError):
        _plan_with_include(police_manifest, ["README.md", "readme.md"], repo_root)


def test_reject_missing_or_untracked_file(
    police_manifest: dict, repo_root: Path
) -> None:
    with pytest.raises(PathViolationError):
        _plan_with_include(police_manifest, ["nonexistent/phantom.txt"], repo_root)


def test_reject_gitlink_entry(police_manifest: dict, repo_root: Path) -> None:
    with pytest.raises(PathViolationError):
        _plan_with_include(
            police_manifest, ["external/copthief-league-protocol"], repo_root
        )


def test_reject_forbidden_git_dir_prefix(
    police_manifest: dict, repo_root: Path
) -> None:
    with pytest.raises(PathViolationError):
        _plan_with_include(police_manifest, [".git/config"], repo_root)


def test_reject_wrong_source_commit(police_manifest: dict, repo_root: Path) -> None:
    bad = dict(police_manifest, source_commit="a" * 40)
    with pytest.raises(ValueError):
        plan(bad, repo_root)


def test_reject_missing_readme(police_manifest: dict, repo_root: Path) -> None:
    no_readme = [p for p in police_manifest["include"] if p != "README.md"]
    with pytest.raises(ManifestError):
        _plan_with_include(police_manifest, no_readme, repo_root)


def test_reject_missing_config_file(police_manifest: dict, repo_root: Path) -> None:
    no_config = [p for p in police_manifest["include"] if not p.startswith("config/")]
    with pytest.raises(ManifestError):
        _plan_with_include(police_manifest, no_config, repo_root)


def test_reject_missing_prd(police_manifest: dict, repo_root: Path) -> None:
    no_prd = [p for p in police_manifest["include"] if p != "docs/PRD.md"]
    with pytest.raises(ManifestError):
        _plan_with_include(police_manifest, no_prd, repo_root)


def test_reject_missing_plan(police_manifest: dict, repo_root: Path) -> None:
    no_plan = [p for p in police_manifest["include"] if p != "docs/PLAN.md"]
    with pytest.raises(ManifestError):
        _plan_with_include(police_manifest, no_plan, repo_root)


def test_reject_missing_todo(police_manifest: dict, repo_root: Path) -> None:
    no_todo = [p for p in police_manifest["include"] if p != "docs/TODO.md"]
    with pytest.raises(ManifestError):
        _plan_with_include(police_manifest, no_todo, repo_root)


def test_reject_unsupported_schema(police_manifest: dict, repo_root: Path) -> None:
    bad = dict(police_manifest, schema="wrong_schema_v99")
    with pytest.raises(ManifestError):
        plan(bad, repo_root)


def test_reject_unsupported_role(police_manifest: dict, repo_root: Path) -> None:
    bad = dict(police_manifest, role="detective")
    with pytest.raises(ManifestError):
        plan(bad, repo_root)


def test_reject_agents_dir_prefix(police_manifest: dict, repo_root: Path) -> None:
    with pytest.raises(PathViolationError):
        _plan_with_include(police_manifest, [".agents/state.json"], repo_root)


def test_reject_sources_dir_prefix(police_manifest: dict, repo_root: Path) -> None:
    with pytest.raises(PathViolationError):
        _plan_with_include(police_manifest, ["sources/private_data.json"], repo_root)


def test_reject_tmp_dir_prefix(police_manifest: dict, repo_root: Path) -> None:
    with pytest.raises(PathViolationError):
        _plan_with_include(police_manifest, ["tmp/cache.db"], repo_root)


def test_reject_credential_filename(police_manifest: dict, repo_root: Path) -> None:
    with pytest.raises(PathViolationError):
        _plan_with_include(police_manifest, ["private.key"], repo_root)


def test_reject_tunnel_config_filename(police_manifest: dict, repo_root: Path) -> None:
    with pytest.raises(PathViolationError):
        _plan_with_include(police_manifest, ["config/prod_tunnel.yml"], repo_root)


def test_pending_counterpart_url_never_treated_as_approval(
    police_manifest: dict, repo_root: Path
) -> None:
    result = plan(police_manifest, repo_root)
    url = result["counterpart_repository_url"]
    assert url == "PENDING_HUMAN_APPROVAL"
    assert not url.startswith("https://")
