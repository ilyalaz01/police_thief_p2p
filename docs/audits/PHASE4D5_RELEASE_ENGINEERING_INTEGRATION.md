# Phase 4D5 — Release Engineering Integration

> Retrospective baseline created after the validated prototype.
> These documents did not exist before the prototype and do not claim otherwise.

Status: **GREEN** for RE-001 and SEC-001 scope only. The public CI suite and every required
quality-gate validator pass. Five clean-worktree environmental skips remain classified separately
and are not evidence for professor-owned or retained-public-evidence checks. This phase does not
claim real-team, uncounted-warm-up, or counted-match readiness.

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
5. `test: normalize artifact AST across Python versions` — retained the accepted `9fbc...` AST
   contract while removing the Python 3.12/3.13 difference in whether `ast.dump()` includes empty
   fields. Production artifact source and the expected contract hash remain unchanged.

## RED evidence (from PR #11 GitHub Actions, before this integration)

| Check | Result |
|---|---|
| `pytest` | FAIL — stale live test references plus the cross-Python AST representation |
| `hcommit_vectors` | FAIL (exit code 4 — the old path was absent from GitHub's current-main PR merge tree) |
| `frozen_manifest` | FAIL (exit code 4 — the old path was absent from the same merge tree) |
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
- `test_public_helpers_constants_signatures_and_moved_ast_are_exact` — **not** a `UnicodeDecodeError`;
  Python 3.12's default `ast.dump()` includes empty AST fields that Python 3.13 omits. The mismatch
  reproduced exactly under the CI-pinned Python 3.12 and disappeared under Python 3.13. A stable
  empty-field-neutral test serializer now produces the original expected `9fbc2558...f26f7cfdf`
  hash on both versions without changing artifact source or the expected hash.

## Final local validation

| Gate | Result |
|---|---|
| Focused offline-ops (`tests/offline_ops`) | PASS — 96/96, 0 skipped |
| Governance (`test_project_governance.py`, `test_quality_evidence.py`, `test_test_architecture.py`) | PASS — 16/16 |
| Windows/cross-Python regression | PASS — all four originally failing cases; AST contract passes on Python 3.12 and 3.13 |
| Full Python 3.12 `uv run pytest` | PASS — 289 passed, 5 classified environmental skips, 0 failed |
| Branch coverage | 94.07%; threshold 85% |
| Ruff `src tests tools/offline_ops` | PASS — zero errors |
| Hcommit golden vectors | PASS — 1 test asserting 5/5 vectors and extra-field binding |
| Pinned conformance kit | PASS — 125/125 across 15 fixtures |
| Frozen production manifest | PASS — 1 test asserting 7/7 exact hashes |
| Python 150-line regression | PASS — zero violations across `src/`, `tests/`, `tools/offline_ops/` |
| Retained-evidence secret scan (`scan-secrets`) | PASS — 0 findings |
| Real composed `quality-gate` | PASS — exit 0; pytest, Ruff, Hcommit, frozen manifest, conformance and secret scan pass; optional `match_artifact` is explicitly skipped because no path was requested |
| GitHub PR #12 quality gate | PASS — Python 3.12, run `32034896295`, job `95402903503` |

## Environmental skips and scope

The five skips in a clean public checkout are one professor-differential check whose private source
is deliberately not distributed and four retained-public-evidence checks whose local evidence is
not part of a fresh clone. They do not block the public RE-001 validators, but they are not relabeled
as executed release evidence. The authorized local evidence workspace must still run them before a
real-team readiness claim.

The fixes did not modify `src/police_thief_lab/**`, game rules, `ScentTacticalPolice` or any
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
- The final committed worktree is clean.
