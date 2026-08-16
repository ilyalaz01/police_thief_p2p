# Phase 4D5 — Release Engineering Integration

> Retrospective baseline created after the validated prototype.
> These documents did not exist before the prototype and do not claim otherwise.

Status: **GREEN** for RE-001 and SEC-001 scope only. This phase does not claim release, real-team,
uncounted-warm-up, or counted-match readiness, and does not claim the wider project suite is fully
green (see Known open item below).

## Accepted state and old branch

- Accepted `origin/main`: `117aca9eced206c53deeb77f6929f1bffce8073c` ("Merge PR #10: make Gatekeeper
  lifecycle race-safe").
- Old partner branch `feature/release-engineering`, HEAD `2d3063f6fb08d6f60bf5f2883dedac9a915b1f35`,
  contained the complete RE-001 implementation but predated the accepted layered-test
  (`tests/unit/`, `tests/integration/`, `tests/system/`) and Gatekeeper-lifecycle-race-safety work
  (PR #9, PR #10).
- Old PR #11 (`feature/release-engineering` -> `main`): confirmed `state: open` via the public
  GitHub API at the time this integration began. Not merged. Closed without merge as part of this
  integration (Step 8); its branch was not rebased, force-pushed, or rewritten.

## Clean-port method

Created `feature/release-engineering-integration` from `origin/main` (exact SHA above, no rebase
or merge of the old branch). Ported only the RE-001-owned paths from the old branch via
`git checkout origin/feature/release-engineering -- <path>` for:

- `.github/workflows/quality-gate.yml`
- `tools/offline_ops/**`
- `tests/offline_ops/**`
- `docs/RELEASE_ENGINEERING.md`

`kickoff.md` and `SOFTWARE_PROJECT_GUIDELINES.md` were deliberately not carried into this branch.
No old flat `tests/test_*.py` file was restored.

## Partner-authored commits on this branch

1. `feat: port RE-001 offline release-engineering workstream to current main` — the clean port
   above.
2. `fix: reconcile release gate with layered tests` — updated `quality_gate.py`'s hardcoded
   `hcommit_vectors`/`frozen_manifest` paths to the current layered locations
   (`tests/integration/test_interop/test_phase4a_crypto_protocol.py`,
   `tests/integration/test_governance/test_frozen_manifest.py`); added an AST-based regression
   test (`tests/offline_ops/test_quality_gate_paths.py`) that fails if a referenced project test is
   moved without updating quality-gate. No Hcommit/frozen logic duplicated.
3. `test: read artifact fixtures explicitly as utf8` — added `encoding="utf-8"` to the four
   `Path.read_text()` calls identified in the three authorized files. No assertion, hash, schema,
   expected byte, fixture, game behavior, artifact, or production source changed.
4. `docs: reconcile RE-001/SEC-001 live documentation with the integration` — updated only the
   RE-001/SEC-001 sections of `docs/TODO.md`, the one RE-001-owned row of
   `docs/GUIDELINES_COMPLIANCE_MATRIX.md`, and added the operator manual to README's documentation
   index.

## RED evidence (from PR #11 GitHub Actions, before this integration)

| Check | Result |
|---|---|
| `pytest` | FAIL |
| `hcommit_vectors` | FAIL (exit code 4 — cause not reproduced locally despite extensive investigation, including a matched-environment Linux/WSL reproduction; documented as a separate, still-open mystery, not addressed by this integration) |
| `frozen_manifest` | FAIL (same exit-code-4 symptom as `hcommit_vectors`) |
| `conformance_kit` | PASS |
| Ruff | PASS |
| `scan_secrets` | PASS |

## Windows cp1255 RED evidence (before Step 4's fix)

Four local Windows failures, confirmed by direct reproduction before any fix was applied:

- `test_reference_artifacts_map_two_exact_group_commits` — `UnicodeDecodeError` (cp1255)
- `test_reference_runtime_artifacts_score_uid_and_consensus_end_to_end[capture-expected_score0]` —
  `UnicodeDecodeError` (cp1255)
- `test_reference_runtime_artifacts_score_uid_and_consensus_end_to_end[survival-expected_score1]` —
  `UnicodeDecodeError` (cp1255)
- `test_public_helpers_constants_signatures_and_moved_ast_are_exact` — **not** a `UnicodeDecodeError**;
  a genuine, pre-existing `AssertionError` (AST-hash mismatch: expected `9fbc2558...f26f7cfdf`,
  actual `7e73215f...cdd1b3`), confirmed identical on Windows and Linux, and confirmed present on
  `origin/main` outside this integration branch. Not caused by encoding, not fixed by Step 4's
  encoding-only change, and out of this step's scope to fix further (would require altering a hash
  or assertion).

## Final local validation

| Gate | Result |
|---|---|
| Focused offline-ops (`tests/offline_ops`) | PASS — 96/96, 0 skipped |
| Governance (`test_project_governance.py`, `test_quality_evidence.py`, `test_test_architecture.py`) | PASS — 16/16 |
| Windows UTF-8 regression (3 authorized files) | 3/4 originally-failing cases now PASS; 1/4 remains RED for the unrelated pre-existing reason above |
| Full `uv run pytest` | 1 failed, 288 passed, 5 skipped |
| Branch coverage | 94.07%; threshold 85% |
| Ruff `src tests tools/offline_ops` | PASS — zero errors |
| Hcommit golden vectors | PASS — 1 test asserting 5/5 vectors and extra-field binding |
| Pinned conformance kit | PASS — 125/125 across 15 fixtures |
| Frozen production manifest | PASS — 1 test asserting 7/7 exact hashes |
| Python 150-line regression | PASS — zero violations across `src/`, `tests/`, `tools/offline_ops/` |
| Retained-evidence secret scan (`scan-secrets`) | PASS — 0 findings |
| Real composed `quality-gate` | **exit 3** — 5 of 6 required checks PASS (`ruff`, `hcommit_vectors`,
  `frozen_manifest`, `conformance_kit`, `scan_secrets`); `match_artifact` correctly `SKIPPED` (no
  `--match-path` given); `pytest` FAILs solely because of the one unrelated, pre-existing,
  out-of-scope AST-hash defect above |

## Known open items (not claimed as passing)

1. `test_public_helpers_constants_signatures_and_moved_ast_are_exact` — pre-existing, platform-
   independent AST-hash mismatch, present on `main` outside this branch, unrelated to RE-001/SEC-001,
   and outside this integration's authorized scope to fix (would require altering a hash/assertion).
   This is why `quality-gate` does not currently reach exit 0.
2. `hcommit_vectors`/`frozen_manifest` reporting `exit code 4` specifically on the original PR #11
   GitHub Actions run — investigated at length (source review, two independent matched-environment
   Linux/WSL reproductions of the exact OS/Python/`uv` versions and every relevant environment
   variable) without reproducing the failure. Cause remains unconfirmed and is not resolved by this
   integration; the reconciled paths in this branch are verified correct and passing both locally
   and via a faithful Linux reproduction.

Neither item required modifying `src/police_thief_lab/**`, game rules, `ScentTacticalPolice` or any
strategy, observation semantics, `MatchProfile`/Hcommit/scent/wire/retry/deadline/duplicate/
equivocation behavior, artifact schemas/bytes/hashes/consensus scope, Rule 47, any frozen file, or
the conformance-kit submodule. No professor-owned or private material was copied. No peer, tunnel,
Gmail, league, or gameplay operation occurred.

## Confirmations

- `kickoff.md` and `SOFTWARE_PROJECT_GUIDELINES.md` are absent from this branch.
- No old flat `tests/test_*.py` file was restored; the accepted layered `tests/unit/`,
  `tests/integration/`, `tests/system/`, and `tests/offline_ops/` architecture and Phase 4D3/4D4
  evidence remain exactly as accepted on `origin/main`.
- No game, strategy, wire, artifact, frozen, external-team, or operational behavior changed.
- The final worktree is clean; only `docs/runbook_prompt.md` remains untracked by design and is not
  part of this branch's history.
