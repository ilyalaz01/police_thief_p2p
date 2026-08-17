"""Govern production documentation, packaging, and declared extension boundaries."""

from __future__ import annotations

import ast
import tomllib
from pathlib import Path

from tests.integration.test_governance.test_frozen_manifest import (
    AUTHORITATIVE_FROZEN_SHA256,
)
from tests.support.project_paths import PROJECT_ROOT

ROOT = PROJECT_ROOT
CODE_ROOTS = (ROOT / "src" / "police_thief_lab", ROOT / "tools")
PUBLIC_PACKAGES = (
    "src/police_thief_lab/__init__.py",
    "src/police_thief_lab/evaluation/__init__.py",
    "src/police_thief_lab/interop/__init__.py",
    "src/police_thief_lab/policies/__init__.py",
    "src/police_thief_lab/presentation/__init__.py",
    "src/police_thief_lab/sdk/__init__.py",
)


def _production_files() -> list[Path]:
    return sorted(path for root in CODE_ROOTS for path in root.rglob("*.py"))


def _relative(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def test_editable_production_symbols_have_docstrings() -> None:
    missing: list[str] = []
    frozen = set(AUTHORITATIVE_FROZEN_SHA256)
    for path in _production_files():
        relative = _relative(path)
        if relative in frozen:
            continue
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=relative)
        if ast.get_docstring(tree) is None:
            missing.append(f"{relative}:1:module")
        for node in ast.walk(tree):
            if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
                if ast.get_docstring(node) is None:
                    missing.append(f"{relative}:{node.lineno}:{node.name}")
    assert missing == []


def test_frozen_docstring_exceptions_have_external_contracts() -> None:
    text = (ROOT / "docs/BUILDING_BLOCK_CONTRACTS.md").read_text(encoding="utf-8")
    assert len(AUTHORITATIVE_FROZEN_SHA256) == 7
    for relative in AUTHORITATIVE_FROZEN_SHA256:
        assert f"`{relative}`" in text
    assert "Frozen inline-docstring exception" in text
    assert "hash-preserving external contract" in text


def test_python_packages_and_public_exports_are_explicit() -> None:
    missing_init = sorted(
        _relative(directory)
        for directory in {path.parent for path in _production_files()}
        if not (directory / "__init__.py").is_file()
    )
    assert missing_init == []
    for relative in PUBLIC_PACKAGES:
        tree = ast.parse((ROOT / relative).read_text(encoding="utf-8"))
        assigned = {
            target.id
            for node in tree.body
            if isinstance(node, ast.Assign)
            for target in node.targets
            if isinstance(target, ast.Name)
        }
        assert "__all__" in assigned


def test_package_metadata_and_dependency_boundary() -> None:
    project = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))["project"]
    assert project["name"] == "police-thief-lab"
    assert project["version"] == "1.0.0"
    assert project["license"] == "MIT"
    assert project["authors"] == [{"name": "Police-Thief P2P Student Team"}]
    assert all("==" in dependency for dependency in project["dependencies"])
    assert (ROOT / "uv.lock").is_file()
    assert not (ROOT / "requirements.txt").exists()


def test_source_uses_package_relative_internal_imports() -> None:
    violations: list[str] = []
    for path in (ROOT / "src" / "police_thief_lab").rglob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.level == 0:
                if (node.module or "").startswith("police_thief_lab"):
                    violations.append(f"{_relative(path)}:{node.lineno}")
            if isinstance(node, ast.Import):
                if any(alias.name.startswith("police_thief_lab") for alias in node.names):
                    violations.append(f"{_relative(path)}:{node.lineno}")
    assert violations == []


def test_building_block_and_extension_contracts_cover_public_boundaries() -> None:
    blocks = (ROOT / "docs/BUILDING_BLOCK_CONTRACTS.md").read_text(encoding="utf-8")
    extensions = (ROOT / "docs/EXTENSION_POINTS.md").read_text(encoding="utf-8")
    package = (ROOT / "docs/PACKAGE_AUDIT.md").read_text(encoding="utf-8")
    for heading in ("Input", "Output", "Setup", "Validation", "Edge behavior"):
        assert heading in blocks
    for service in (
        "DomainSDK", "PoliciesSDK", "EvaluationSDK", "ArtifactsSDK", "TransportSDK",
        "ConfigurationSDK",
    ):
        assert service in blocks
    for extension in (
        "DecisionBackend", "ScentModel", "PolicyFactory", "MatchProfile",
        "plugins", "hooks", "middleware",
    ):
        assert extension in extensions
    assert "Observation-only" in extensions
    assert "explicit bilateral agreement" in extensions
    assert "uv-only" in package
    assert "No dependency change" in package
