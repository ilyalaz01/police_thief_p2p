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

## Phase 4D1A.1 reproducibility correction

The recorded digest was independently reproduced from Phase 4D0 Git objects and the current
split files. The canonical preimage is framed as follows:

1. Read `tests/test_phase4a_interop.py` and `tests/test_phase4b_transport.py` from Git object
   `f28895debe3762e3905602d37a040ace7cb9234d`; read the 12 current files listed in the mapping
   above from the worktree.
2. Walk each parsed module with `ast.walk`. For every `FunctionDef` or `AsyncFunctionDef`, emit
   `{"kind": type(node).__name__, "name": node.name, "dump": ast.dump(node,
   include_attributes=False)}`. Classes are not separate entries, but their methods are found by
   the walk.
3. Sort the complete entry multiset by `(name, kind, dump)`. Serialize the one enclosing array
   with `json.dumps(entries, ensure_ascii=False, sort_keys=True, separators=(",", ":"))`.
4. UTF-8 encode that single JSON string. JSON commas delimit entries; there is no additional
   record delimiter and no final newline. SHA-256 is computed over those exact bytes.

This produces 46 entries and
`dba16e31190e505495bf00406335613d3cbbaf4b35765325bd5844cbe2a9a012` for both sides. Phase
4D1A.1 also added a governance regression for backticked paths in live documents and corrected
the stale live Phase 4A/4B references. The original filenames remain above because this audit
intentionally records the source-to-destination mapping.

Correction validation: 136/136 tests passed with no skips or xfails; configured branch coverage
remained 90.81%; governance passed 7/7; Ruff was clean; Hcommit remained 5/5; conformance remained
125/125; and the frozen manifest remained 7/7. Split test/support counts remained at most 142,
the over-150 roster remained the same four production files, and the Phase 4D1A accepted-base
diff contained no forbidden source, external, interoperability, dependency, lockfile, or split
test/support changes.
