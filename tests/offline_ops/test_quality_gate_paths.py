"""quality-gate's hardcoded project-test paths must exist in this layout.

If a referenced test file is moved/renamed without updating
quality_gate.py, this test fails immediately instead of quality-gate
silently reporting a false VALIDATOR_UNAVAILABLE for a validator that
still genuinely exists, just somewhere else.
"""

from __future__ import annotations

import ast
from pathlib import Path

from tools.offline_ops.commands.quality_gate import _SUBPROCESS_CHECKS

_REPO_ROOT = Path(__file__).resolve().parents[2]


def _referenced_node_ids() -> list[str]:
    return [
        arg
        for _check_id, argv in _SUBPROCESS_CHECKS
        for arg in argv
        if arg.startswith("tests/") and "::" in arg
    ]


def test_at_least_the_two_pinned_project_test_node_ids_are_checked() -> None:
    node_ids = _referenced_node_ids()
    assert len(node_ids) >= 2


def test_every_referenced_project_test_path_exists_and_defines_the_function() -> None:
    for node_id in _referenced_node_ids():
        file_part, _, function_name = node_id.partition("::")
        path = _REPO_ROOT / file_part
        assert path.is_file(), f"quality-gate references a missing file: {file_part}"

        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        defined = {
            node.name
            for node in ast.walk(tree)
            if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef)
        }
        assert function_name in defined, (
            f"quality-gate references {node_id}, but {function_name} is not "
            f"defined in {file_part}"
        )
