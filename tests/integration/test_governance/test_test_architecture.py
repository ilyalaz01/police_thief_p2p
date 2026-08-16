"""RED contract for the guideline-required test architecture."""

from __future__ import annotations

from pathlib import Path


def _project_root() -> Path:
    for candidate in Path(__file__).resolve().parents:
        if (candidate / "pyproject.toml").is_file():
            return candidate
    raise AssertionError("project root not found")


ROOT = _project_root()
TESTS = ROOT / "tests"
CORE_LAYERS = {"unit", "integration", "system"}
LEGACY_SUPPORT = {
    "artifact_contract_hashes.py",
    "artifact_contract_support.py",
    "interop_test_support.py",
}


def test_required_test_layers_and_shared_fixture_module_exist() -> None:
    assert all((TESTS / layer).is_dir() for layer in CORE_LAYERS)
    assert (TESTS / "support").is_dir()
    assert (TESTS / "conftest.py").is_file()


def test_core_tests_are_not_left_in_the_flat_legacy_layout() -> None:
    unlayered = sorted(
        path.relative_to(TESTS).as_posix()
        for path in TESTS.rglob("test_*.py")
        if path.relative_to(TESTS).parts[0] not in CORE_LAYERS | {"offline_ops"}
    )
    assert unlayered == []


def test_shared_support_is_not_left_at_the_test_root() -> None:
    assert not any((TESTS / name).exists() for name in LEGACY_SUPPORT)


def test_layer_boundaries_and_source_mapping_are_documented() -> None:
    testing = (ROOT / "docs" / "TESTING.md").read_text(encoding="utf-8")
    for required in (
        "Unit tests",
        "Integration tests",
        "System tests",
        "Shared fixtures",
        "Source-to-test map",
        "tests/offline_ops",
    ):
        assert required in testing
