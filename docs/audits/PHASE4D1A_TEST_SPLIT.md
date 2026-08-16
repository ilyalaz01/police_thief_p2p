# Phase 4D1A — REF-001 Mechanical Interoperability Test Split

Result: **GREEN test-only slice**. REF-001 remains **IN_PROGRESS** because four unchanged
production files still exceed 150 counted lines. TST-001 remains **PLANNED**; broader test-layer
restructuring was outside this slice.

## Commits and mapping

- `9a13ac4` — `test: split phase4a interoperability checks`
- `784b5cb` — `test: split phase4b transport checks`
- `docs: record phase4d1a test split evidence` — this acceptance-report commit

| Original | Resulting modules |
|---|---|
| `tests/test_phase4a_interop.py` (305) | `test_phase4a_crypto_protocol.py` (33), `test_phase4a_boundary_audit_artifacts.py` (52), `test_phase4a_runtime_network.py` (91), `test_phase4a_runtime_rules.py` (79), `test_phase4a_process.py` (42) |
| `tests/test_phase4b_transport.py` (441) | `test_phase4b_network.py` (127), `test_phase4b_artifact_builders.py` (104), `test_phase4b_identity_gates.py` (142), `test_phase4b_runtime_artifacts.py` (95), `test_phase4b_artifact_commits.py` (42), `test_phase4b_cli_preflight.py` (41) |
| shared helpers | `tests/interop_test_support.py` (108); frame, profile, and free-port logic occur once |

The original modules were removed. Count means nonblank lines whose first non-whitespace
character is not `#`.

## Before/after identity evidence

- Full characterization before editing: 135 collected and 135 passed, no skip/xfail, 90.81%
  configured branch coverage.
- `pytest --collect-only -q --no-cov`: 135 before and 135 after. Removing only the source-file
  prefix from each node ID produced identical multisets, including every parameterized case.
- AST manifest: every `FunctionDef`/`AsyncFunctionDef` in the two originals, including nested
  functions and methods, serialized with `ast.dump(..., include_attributes=False)` and compared
  as a path-independent sorted multiset. Before and after both contain 46 entries and SHA-256
  `dba16e31190e505495bf00406335613d3cbbaf4b35765325bd5844cbe2a9a012`.
- No assertion, fixture, parameterization, mark, test function, timeout, retry, or sleep changed.
  Imports, formatting, and module docstrings changed only as required by the moves and Ruff.

## Acceptance gates

| Gate | Result |
|---|---|
| Full suite | PASS — 135/135, no skip/xfail |
| Configured branch coverage | PASS — 90.81% (≥90.80%, ≥85% floor) |
| Ruff `src tests` | PASS — zero errors |
| Hcommit golden vectors | PASS — 5/5 |
| Pinned conformance | PASS — 125/125 |
| Frozen manifest | PASS — 7/7 |
| Governance | PASS — 6/6 |
| New test/support line ceiling | PASS — maximum 142 |
| Phase 4D0-base forbidden-path diff | PASS — no `src/`, `external/`, `interop/`, `pyproject.toml`, or `uv.lock` changes |

The repository-wide over-150 roster is now exactly the four unchanged production files:

- `src/police_thief_lab/interop/runtime.py` — 565
- `src/police_thief_lab/policies/phase3b.py` — 303
- `src/police_thief_lab/interop/artifacts.py` — 168
- `src/police_thief_lab/policies/belief.py` — 154

No production, frozen, profile, serialization-domain, artifact, policy, runtime, crypto,
transport, gameplay, external, fixture/vector/log, dependency, or lockfile behavior changed.
No network, external contact, gameplay, merge, push, or tag occurred. Production proposals remain
unselected; this report ends the Phase 4D1A slice.
