# Phase 4D8 — Package, Building-Block, and Extension Contracts

> Retrospective baseline created after the validated prototype.
> These documents did not exist before the prototype and do not claim otherwise.

Status: **GREEN**. `DOCS-002`, `PKG-001`, `EXT-001`, and the reconciled `ISO-001` are DONE.
`COST-001` remains IN_PROGRESS because CPU, RAM, and latency have not yet been measured.

## Authority and scope

The phase was derived from Software Project Guidelines sections 2.3, 11, 13, 15, and 16, then
bounded by `RULES_AND_INTEROP_BASELINE.md`, the seven-file frozen manifest, existing SDK/CLI
contracts, and the current TODO. It adds documentation/package evidence only. It does not introduce
or select a game rule, strategy, scent model, profile term, wire field, artifact field, consensus
scope, or external-operation policy.

## TDD evidence

RED commit `0374799` added six governance tests. The initial run produced **4 failed, 2 passed**:

- 154 editable production symbols lacked inline docstrings;
- the building-block, extension, and package audit documents were absent;
- package author metadata was absent;
- package layout and relative internal-import checks were already green.

GREEN commit `7506229` added the contracts, team-level metadata, exact inventory, and inline
docstrings. It moved only the legacy `write_artifacts` implementation into
`interop/artifact_writers.py` so adding documentation did not break the 150-line limit; the
established import, annotations, signature, filenames, ordering, and bytes remain characterized.

The first full run exposed one living-document compatibility error: 328 tests passed and one test
failed because the accepted literal `GUI-001: DONE` had been reformatted. Correction commit
`42c98cb` restored that exact wording. The targeted correction passed 17/17 and the repeated full
suite passed 329/329. This failure is retained rather than relabeled as an initial pass.

## Documentation inventory

- Production Python files scanned: 88 (`src`: 65; `tools`: 23).
- Classes/functions/methods scanned: 365.
- Editable symbols governed inline: 306; missing docstrings after GREEN: 0.
- Symbols in the exact seven frozen files: 59; their external contracts are in
  `docs/BUILDING_BLOCK_CONTRACTS.md`.
- Frozen exceptions are derived from `AUTHORITATIVE_FROZEN_SHA256`; the list cannot grow silently.
- Files over 150 counted lines across `src` and tests: 0; maximum is exactly 150 in an unchanged
  configuration test. `artifacts.py` is 140 and the new writer module is 20 counted lines.

Tests remain executable specifications with descriptive names. The automated inline inventory is
intentionally production-scoped; adding hundreds of redundant test-function docstrings would add
line-limit churn without improving the test contracts.

## Package and extension result

- `pyproject.toml` now contains non-personal team author metadata; MIT license, package version,
  exact runtime dependency, and uv lock remain coherent.
- Every production package directory has `__init__.py`; public boundaries retain explicit
  `__all__`; internal package imports are relative.
- No dependency or lockfile changed.
- `DecisionBackend`, `ScentModel`, `PolicyFactory`, evaluation scenarios, and `MatchProfile` have
  explicit lifecycle and compatibility contracts.
- Dynamic competitive-runtime plugins and mutation hooks are explicitly inapplicable. The
  `ApiGatekeeper` remains the only external-call middleware.
- Extensions cannot bypass `Observation`, promote a new champion, or turn omission into agreement.

## Validation

| Check | Result |
|---|---|
| Phase 4D8 governance | PASS — 6/6 |
| Artifact API/AST/byte compatibility | PASS — 4/4 |
| Full pytest after correction | PASS — 329/329 |
| Branch coverage | PASS — 92.52% (threshold 85%) |
| Ruff `src tests tools` | PASS — zero errors |
| Hcommit golden vectors | PASS — 5/5 |
| Frozen production manifest | PASS — 7/7 exact |
| MIT conformance kit | PASS — 125/125 |
| Editable production docstrings | PASS — 0 missing among 306 |
| Python 150-line gate | PASS — 0 violations |
| Clean tracked secret scan under quality-gate policy | PASS — zero findings |
| Final worktree before evidence files | PASS — clean |

The direct scanner intentionally has no implicit exclusions. When invoked on the clean snapshot
without the quality-gate policy, it found eight synthetic credential-like fixtures under
`tests/offline_ops`; this is the scanner's own RED test data. The composed gate excludes exactly
that known-safe directory. With the same exact exclusion, the clean tracked snapshot passed with
zero findings. Neither invocation printed or retained matched values. Long-lived ignored Phase 4B
evidence was outside the tracked snapshot and remains local.

## Proven versus not proven

Proven: editable production documentation completeness, exact frozen exception equality, package
metadata/exports/import boundaries, extension applicability, artifact compatibility, full local
regression, coverage, lint, hashes, and conformance.

Not proven and not claimed: historical pre-code TDD, ISO certification, exhaustive mathematical
duplicate detection, CPU/RAM/public latency, final two-repository submission, bilateral approval,
another-team compatibility, public transport readiness, Gmail reporting, or counted play.

## Operational hard stop

No peer, simulator game, public request, tunnel, Gmail action, external-team contact, warm-up,
league report, counted game, new AI/ML/search, submission repository, or tag was started. The frozen
`ScentTacticalPolice`, physics, scent, Hcommit, MCP, wire, artifact, tie, and consensus semantics did
not change.

The smallest safe next offline milestone is `RES-001` + `VIS-001`: publish a deterministic,
public-safe sensitivity dataset and reproducible notebook/figures without changing the champion.
