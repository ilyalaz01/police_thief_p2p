# Phase 4D12A — Role Repository Content Boundary

Status: **GREEN locally; PR quality-gate acceptance required before merge**.

Classification: `OFFLINE_SUBMISSION_CONTENT_POLICY`.

## Outcome

Phase 4D12A selects a deterministic candidate regular-file boundary for the future Police and
Thief repositories. It advances `SUB-001` from PLANNED to IN_PROGRESS but does not claim final
repository readiness.

The policy satisfies the Rule 50 minimum in both candidate sets and retains the verified public
engine, tests, GUI/Replay, quality tooling, documents, and research evidence. Rule 49 remains
incomplete because actual role READMEs, reciprocal URLs, repositories, and final tags do not exist.

## Source and authority review

The phase rechecked official Rules 49 and 50, `RULES_AND_INTEROP_BASELINE.md`, PRD/PLAN/TODO,
official-readiness and release/Git governance, the real tracked index, the current runtime policy
construction, and the independent partner export-tool scope.

Generic submission structure cannot alter frozen or negotiated behavior. No game, profile, wire,
artifact, strategy, or interoperability rule is reinterpreted by the content policy.

## Decisions

- Both role repositories preserve one verified shared implementation instead of creating divergent
  engine copies.
- Police remains the frozen accepted `ScentTacticalPolice`.
- Thief is recorded as the current runtime default `RandomLegalThief`, explicitly not a new
  champion decision.
- Ignored/private sources and every forbidden operator path remain outside the candidate.
- `tests/offline_ops/` is excluded because it intentionally contains synthetic secret-shaped
  scanner fixtures; `tools/offline_ops/` remains.
- The exporter excludes `.gitmodules` and the conformance-kit gitlink. The approved MIT submodule
  must be restored/pinned separately before each final role gate.
- Snapshot export validates bytes but does not replace shared Git history or contributor authorship.

## TDD evidence

RED commit `03031ce` added five policy contracts first. All five failed because the JSON policy and
its explanatory document did not yet exist. The test itself was Ruff-clean and 112 counted lines.

GREEN commit `2181c66` added only the machine-readable policy and documentation. Focused result:
5/5. No production source, dependency, lockfile, frozen file, or partner-owned exporter path changed.

The first full run produced 352 passes and one expected lifecycle assertion: the Phase 4D11 guard
still required `SUB-001` to remain PLANNED. It now reads the exact SUB-001 block, requires
IN_PROGRESS, and continues to forbid premature DONE. The combined policy/Git/project governance
subset passed 18/18 before the final full rerun.

## Acceptance boundary

Accept only the candidate content-policy slice after the final validation below and public PR CI
are green. Do not accept `SUB-001` as DONE until the exporter is integrated, two actual role trees
are independently validated, reciprocal URLs are approved, both remotes exist, and reviewed final
tags point to the exact accepted commits.

## Remaining steps

1. Review and integrate the independent partner submission-export implementation.
2. Generate exact ignored manifests from the final accepted shared commit and reproduce both plans.
3. Create offline history-preserving role branches and role-specific README overlays.
4. Obtain exact URL/content approval before any final remote or tag operation.

No peer, tunnel, public request, opponent contact, Gmail, gameplay, counted operation, final remote,
publication, or tag occurred.

## Final validation

- Full suite: 353/353 passed, no skips or xfails.
- Combined statement/branch coverage: 92.58684863523573% (threshold: 85%).
- Focused policy contract: 5/5; combined policy/Git/project governance: 18/18.
- Ruff over `src`, `tests`, and `tools`: zero errors.
- Hcommit golden vectors: 5/5; authoritative frozen manifest: 7/7.
- MIT conformance kit: 125/125.
- Staged public snapshot under the documented CI scanner policy: PASS, zero findings.
- Candidate policy resolves to 271 tracked regular files at the accepted branch state.
- New Python test: 112 counted lines; production-source and partner-exporter diffs: empty.

The scanner policy excludes `tests/offline_ops/`, whose synthetic secret-shaped fixtures are
already disclosed and directly tested in the shared repository. No matched value was retained.
The adjacent JSON contains the same machine-readable decision and exact counts.
